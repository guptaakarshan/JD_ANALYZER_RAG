from fastapi import FastAPI,UploadFile, File
import shutil
import os

from rag.extractor import load_pdf_documents
from rag.chunker import split_documents
from rag.embeddings import create_embeddings

app = FastAPI()

UPLOAD_DIR="uploads"

os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.get("/")
def home():
    return {
        "message": "JD Analyzer Backend Running"
    }

@app.post("/upload")

async def upload_pdf(file: UploadFile = File(...)):
    
    if not file.filename.endswith(".pdf"):
        return {
            "error": "Only PDF files are allowed"
        }
    
    file_path=f"{UPLOAD_DIR}/{file.filename}"
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    try:
        documents = load_pdf_documents(file_path)
        
        chunked_documents = split_documents(documents)
        
        embeddings=create_embeddings(chunked_documents)
        
        return {
        "filename": file.filename,
        "total_original_pages": len(documents),
        "total_chunks": len(chunked_documents),
        "total_embeddings": len(embeddings),
        "embedding_dimensions": len(embeddings[0]),
    }
        
    except Exception as e:
        return {
            "error": str(e)
        }