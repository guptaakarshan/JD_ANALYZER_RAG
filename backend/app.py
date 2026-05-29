from fastapi import FastAPI, UploadFile, File
import shutil
import os

from rag.extractor import load_pdf_documents
from rag.chunker import split_documents
from rag.vectorstore import create_vector_store

app = FastAPI()

UPLOAD_DIR = "uploads"

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

    file_path = f"{UPLOAD_DIR}/{file.filename}"

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:

        # 1. Load PDF
        documents = load_pdf_documents(file_path)

        # 2. Split into chunks
        chunked_documents = split_documents(documents)
        
        # we deleted the embedding file because FAISS automatically creates the embeddings, we dont have to do it again manually

        # 3. Create FAISS vector store
        vector_store = create_vector_store(
            chunked_documents
        )


        return {
            "filename": file.filename,
            "total_pages": len(documents),
            "total_chunks": len(chunked_documents),
            "vector_store_created": True,
            "faiss_index_location": "faiss_index/"
        }

    except Exception as e:

        return {
            "error": str(e)
        }