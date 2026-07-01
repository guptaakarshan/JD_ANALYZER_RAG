from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import shutil
import os

from rag.extractor import load_pdf_documents
from rag.chunker import split_documents
from rag.vectorstore import create_vector_store
from rag.retriever import retrieve_documents
from rag.rag_chain import generate_answer
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

class JDRequest(BaseModel):
    job_description: str


@app.get("/")
def home():
    return {
        "message": "JD Analyzer Backend Running"
    }


@app.post("/upload-pdf")
async def upload_pdf(file: UploadFile = File(...)):

    if not file.filename.endswith(".pdf"):
        return {
            "error": "Only PDF files are allowed"
        }

    file_path = f"{UPLOAD_DIR}/{file.filename}"

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:

        # 1. Load PDF
        documents = load_pdf_documents(file_path)

        # 2. Split into chunks
        chunked_documents = split_documents(documents)
        
        
       # print("\n========== PDF CHUNKS ==========\n")

        #for i, chunk in enumerate(chunked_documents):

         # print(f"Length: {len(chunk.page_content)}")
           # print(chunk.page_content)

        #print("\n===============================\n")
        
        
        # we deleted the embedding file because FAISS automatically creates the embeddings, we dont have to do it again manually

        # 3. Create FAISS vector store
        create_vector_store(
            chunked_documents,
            "resume_faiss_index"
        )
        
        os.remove(file_path)

        return {
            "filename": file.filename,
            "total_pages": len(documents),
            "total_chunks": len(chunked_documents),
            "vector_store_created": True,
            "faiss_index_location": "resume_faiss_index/"
        }
    except Exception as e:
        return {
            "error": str(e)
        }
        
        
@app.post("/upload-jd")

def upload_jd(request: JDRequest):
    
    try:
        
        documents=[
            Document(
                page_content=request.job_description
            )
        ]
        
        chunked_documents=split_documents(documents)
        
       # print("\n========== JD CHUNKS ==========\n")

        #for i, chunk in enumerate(chunked_documents):

          #  print(f"\n------ CHUNK {i+1} ------")
           # print(f"Length: {len(chunk.page_content)}")
            #print(chunk.page_content)

        #print("\n===============================\n")
        
        create_vector_store(
            chunked_documents,
            "jd_faiss_index"
        )
        
        return{
            "message":"Job Description Uploaded",
            "total_chunks":len(chunked_documents)
        }
    except Exception as e:
            return {
                "error": str(e)
            }

@app.post("/search")
def search_documents(request: SearchRequest):
    try:
        results = retrieve_documents(
            request.query,
            "resume_faiss_index"
        )

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

    results = retrieve_documents(
        request.query,
        "jd_faiss_index"
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
    
@app.post("/ask")
def ask_question(request: SearchRequest):

    try:

        answer = generate_answer(
            request.query
        )

        return {
            "question": request.query,
            "answer": answer
        }
        
    except Exception as e:
        return {"error": str(e)}