#  Multi-Document RAG-Based JD Analyzer

A Retrieval-Augmented Generation (RAG) application that analyzes a candidate's resume against a job description and answers context-aware questions using Large Language Models (LLMs).

The system allows users to upload a resume (PDF), provide a job description (text), and ask natural language questions such as:

* Am I suitable for this role?
* Which skills from my resume match the JD?
* Which projects are relevant to this position?
* What qualifications are required for this role?

---

## 📌 Features

* Resume PDF Upload & Processing
* Job Description Text Upload
* PDF Text Extraction using LangChain
* Intelligent Document Chunking
* OpenAI Embeddings Generation
* FAISS Vector Database Integration
* Semantic Search & Retrieval
* Multi-Document RAG Pipeline
* LLM-Powered Question Answering
* FastAPI REST API Backend

---

## 🏗️ Architecture

Resume PDF
↓
PDF Loader
↓
Chunking
↓
OpenAI Embeddings
↓
FAISS Vector Store

Job Description Text
↓
Document Creation
↓
Chunking
↓
OpenAI Embeddings
↓
FAISS Vector Store

User Question
↓
Resume Retrieval
+
JD Retrieval
↓
Prompt Template
↓
LLM
↓
Generated Answer

---

## 🛠️ Tech Stack

### Backend

* Python
* FastAPI

### RAG Framework

* LangChain

### Vector Database

* FAISS

### Embedding Model

* OpenAI Embeddings (`text-embedding-3-small`)

### LLM

* OpenAI GPT Models

### Utilities

* Pydantic
* PyPDFLoader
* dotenv

---

## 📂 Project Structure

backend/

├── app.py

├── rag/

│   ├── extractor.py

│   ├── chunker.py

│   ├── vectorstore.py

│   ├── retriever.py

│   ├── llm.py

│   └── rag_chain.py

├── resume_faiss_index/

├── jd_faiss_index/

├── uploads/

├── requirements.txt

└── .env

---

## ⚙️ Installation

### 1. Clone Repository

```bash
git clone <your-repository-url>
cd JD-analyzer_RAG
```

### 2. Create Virtual Environment

```bash
python -m venv venv
```

### Activate Environment

Windows:

```bash
venv\Scripts\activate
```

Mac/Linux:

```bash
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Create .env File

```env
OPENAI_API_KEY=your_openai_api_key
```

### 5. Run Application

```bash
uvicorn app:app --reload
```

Open Swagger UI:

```text
http://127.0.0.1:8000/docs
```

---

## 📡 API Endpoints

### Upload Resume

```http
POST /upload-pdf
```

Upload a resume PDF and create a FAISS vector store.

---

### Upload Job Description

```http
POST /upload-jd
```

Example Request:

```json
{
  "job_description": "We are looking for a Full Stack Developer with React, Node.js, MongoDB and Git experience."
}
```

---

### Search Resume Chunks

```http
POST /search
```

---

### Search JD Chunks

```http
POST /search-jd
```

---

### Ask Questions

```http
POST /ask
```

Example:

```json
{
  "query": "Which skills from my resume match the job description?"
}
```

---

## 💡 Example Questions

* What projects has the candidate built?
* Which skills match the job description?
* Am I suitable for this role?
* What technologies does the candidate know?
* Which projects are most relevant to this job?

---

## 📚 Key Concepts Implemented

* Retrieval-Augmented Generation (RAG)
* Semantic Search
* Vector Embeddings
* Document Chunking
* FAISS Vector Database
* Multi-Document Retrieval
* Prompt Engineering
* LLM-Based Question Answering

---

## 🚀 Future Improvements

* ATS Score Generation
* Skill Gap Analysis
* Resume Improvement Suggestions
* Chat-Based UI
* Authentication & User Profiles
* Support for Multiple Resumes
* Cloud Deployment

---


⭐ If you found this project useful, consider giving it a star!
