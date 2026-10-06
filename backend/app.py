from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import shutil
import os
from uuid import uuid4
from pathlib import Path

from rag.extractor import load_pdf_documents
from rag.chunker import split_documents
from rag.vectorstore import create_vector_store
from rag.retriever import retrieve_documents
from rag.rag_chain import generate_answer
from rag.session_store import get_session_paths, read_metadata, write_metadata
from rag.skill_matcher import analyze_candidate_fit, extract_skills
from pydantic import BaseModel
from langchain_core.documents import Document

app = FastAPI()

BASE_DIR = Path(__file__).resolve().parent

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:5174",
    "http://127.0.0.1:5174",
    "https://jd-analyzer-rag.vercel.app",
    "https://jd-analyzer.akarshan.dev"
],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "uploads"

os.makedirs(UPLOAD_DIR, exist_ok=True)


class SearchRequest(BaseModel):
    query: str
    session_id: str | None = None

class JDRequest(BaseModel):
    job_description: str
    session_id: str | None = None


@app.get("/")
def home():
    return {
        "message": "JD Analyzer Backend Running"
    }


@app.post("/upload-pdf")
async def upload_pdf(file: UploadFile = File(...), session_id: str | None = None):

    if not file.filename.endswith(".pdf"):
        return {
            "error": "Only PDF files are allowed"
        }

    session_id = session_id or str(uuid4())
    resume_index_path, jd_index_path, metadata_path = get_session_paths(session_id, base_dir=BASE_DIR)
    session_dir = resume_index_path.parent
    session_dir.mkdir(parents=True, exist_ok=True)

    file_path = session_dir / file.filename

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        documents = load_pdf_documents(str(file_path))
        chunked_documents = split_documents(documents, document_type="resume")
        resume_text = "\n".join(document.page_content for document in documents)
        resume_skills = extract_skills(resume_text)
        existing_metadata = read_metadata(session_id, base_dir=BASE_DIR)
        jd_skills = existing_metadata.get("jd_skills", [])
        jd_text = existing_metadata.get("jd_text", "")

        create_vector_store(
            chunked_documents,
            str(resume_index_path)
        )

        write_metadata(
            session_id,
            {
                "session_id": session_id,
                "resume_filename": file.filename,
                "resume_index_path": str(resume_index_path),
                "jd_index_path": str(jd_index_path),
                "metadata_path": str(metadata_path),
                "resume_skills": resume_skills,
                "resume_text": resume_text,
            },
            base_dir=BASE_DIR,
        )

        os.remove(file_path)

        return {
            "session_id": session_id,
            "filename": file.filename,
            "total_pages": len(documents),
            "total_chunks": len(chunked_documents),
            "vector_store_created": True,
            "faiss_index_location": str(resume_index_path),
            "skill_insights": analyze_candidate_fit(resume_text, jd_text),
        }
    except Exception as e:
        return {
            "error": str(e)
        }
        
        
@app.post("/upload-jd")
def upload_jd(request: JDRequest):
    try:
        session_id = request.session_id or str(uuid4())
        resume_index_path, jd_index_path, metadata_path = get_session_paths(session_id, base_dir=BASE_DIR)
        session_dir = jd_index_path.parent
        session_dir.mkdir(parents=True, exist_ok=True)

        documents = [Document(page_content=request.job_description)]
        chunked_documents = split_documents(documents, document_type="jd")
        jd_skills = extract_skills(request.job_description)
        existing_metadata = read_metadata(session_id, base_dir=BASE_DIR)
        resume_skills = existing_metadata.get("resume_skills", [])
        resume_text = existing_metadata.get("resume_text", "")

        create_vector_store(
            chunked_documents,
            str(jd_index_path)
        )

        write_metadata(
            session_id,
            {
                "session_id": session_id,
                "jd_index_path": str(jd_index_path),
                "resume_index_path": str(resume_index_path),
                "metadata_path": str(metadata_path),
                "jd_skills": jd_skills,
                "jd_text": request.job_description,
            },
            base_dir=BASE_DIR,
        )

        return {
            "session_id": session_id,
            "message": "Job Description Uploaded",
            "total_chunks": len(chunked_documents),
            "skill_insights": analyze_candidate_fit(resume_text, request.job_description),
        }
    except Exception as e:
            return {
                "error": str(e)
            }

@app.post("/search")
def search_documents(request: SearchRequest):
    try:
        if not request.session_id:
            return {"error": "session_id is required"}

        resume_index_path, _, _ = get_session_paths(request.session_id, base_dir=BASE_DIR)
        results = retrieve_documents(request.query, str(resume_index_path))

        return {
            "query": request.query,
            "results": [
                {
                    "content":doc.page_content,
                    "score":float(score)
                }
                for doc, score in results
                    
            ]
        }
    except Exception as e:

        return {
            "error": str(e)
        }
        
@app.post("/search-jd")
def search_jd(request: SearchRequest):
    if not request.session_id:
        return {"error": "session_id is required"}

    _, jd_index_path, _ = get_session_paths(request.session_id, base_dir=BASE_DIR)
    results = retrieve_documents(request.query, str(jd_index_path))

    return {
        "results": [
            {
                "content": doc.page_content,
                "score": float(score)
            }
            for doc, score in results
        ]
    }
    
@app.post("/ask")
def ask_question(request: SearchRequest):

    try:
        if not request.session_id:
            return {"error": "session_id is required"}

        result = generate_answer(request.query, request.session_id)

        return {
            "question": request.query,
            **result,
        }
        
    except Exception as e:
        return {"error": str(e)}