from fastapi import FastAPI, UploadFile, File, Form, Request
from fastapi.middleware.cors import CORSMiddleware
import shutil
import os
from uuid import uuid4

from rag.extractor import load_pdf_documents
from rag.chunker import split_documents
from rag.vectorstore import create_vector_store
from rag.retriever import retrieve_documents
from rag.rag_chain import generate_answer
from rag.session_store import get_session_paths
from rag.candidate_scorer import calculate_candidate_fit
from pydantic import BaseModel
from langchain_core.documents import Document

app = FastAPI()

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
async def upload_pdf(
    request: Request,
    file: UploadFile = File(...),
    session_id: str | None = Form(None)
):

    if not file.filename.endswith(".pdf"):
        return {
            "error": "Only PDF files are allowed"
        }

    resolved_session_id = session_id or request.query_params.get("session_id") or str(uuid4())
    resume_index_path, _, _ = get_session_paths(resolved_session_id)

    file_path = f"{UPLOAD_DIR}/{file.filename}"

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:

        # 1. Load PDF
        documents = load_pdf_documents(file_path)

        # 2. Split into chunks
        chunked_documents = split_documents(documents, document_type="resume")

        # 3. Create FAISS vector store
        create_vector_store(
            chunked_documents,
            str(resume_index_path)
        )
        
        os.remove(file_path)

        return {
            "session_id": resolved_session_id,
            "filename": file.filename,
            "total_pages": len(documents),
            "total_chunks": len(chunked_documents),
            "vector_store_created": True,
            "faiss_index_location": str(resume_index_path)
        }
    except Exception as e:
        if os.path.exists(file_path):
            os.remove(file_path)
        return {
            "error": str(e)
        }
        
        
@app.post("/upload-jd")
def upload_jd(request: JDRequest):
    
    try:
        session_id = request.session_id or str(uuid4())
        _, jd_index_path, _ = get_session_paths(session_id)
        
        documents = [
            Document(
                page_content=request.job_description,
                metadata={"source": "job_description", "page": 0}
            )
        ]
        
        chunked_documents = split_documents(documents, document_type="jd")
        
        create_vector_store(
            chunked_documents,
            str(jd_index_path)
        )
        
        return {
            "session_id": session_id,
            "message": "Job Description Uploaded",
            "total_chunks": len(chunked_documents)
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

        resume_index_path, _, _ = get_session_paths(request.session_id)
        results = retrieve_documents(
            request.query,
            str(resume_index_path)
        )

        return {
            "query": request.query,
            "results": [
                {
                    "content": doc.page_content,
                    "score": float(score)
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
    try:
        if not request.session_id:
            return {"error": "session_id is required"}

        _, jd_index_path, _ = get_session_paths(request.session_id)
        results = retrieve_documents(
            request.query,
            str(jd_index_path)
        )

        return {
            "results": [
                {
                    "content": doc.page_content,
                    "score": float(score)
                }
                for doc, score in results
            ]
        }
    except Exception as e:
        return {
            "error": str(e)
        }
    
@app.post("/ask")
def ask_question(request: SearchRequest):

    try:
        if not request.session_id:
            return {"error": "session_id is required"}

        result = generate_answer(
            request.query,
            request.session_id
        )

        return {
            "question": request.query,
            "answer": result["answer"],
            "sources": result["sources"],
            "retrieval_stats": result["retrieval_stats"],
        }
        
    except Exception as e:
        return {"error": str(e)}


class AnalyzeMatchRequest(BaseModel):
    session_id: str


@app.post("/analyze-match")
def analyze_match(request: AnalyzeMatchRequest):
    try:
        if not request.session_id:
            return {"error": "session_id is required"}

        return calculate_candidate_fit(request.session_id)
    except Exception as e:
        return {"error": str(e)}