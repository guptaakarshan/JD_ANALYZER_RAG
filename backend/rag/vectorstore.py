from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv

load_dotenv()

embedding_model=OpenAIEmbeddings(
  model="text-embedding-3-small"
)

def create_vector_store(chunked_documents):
  vector_store=FAISS.from_documents(
    documents=chunked_documents,
    embedding=embedding_model
  )
  
  vector_store.save_local("faiss_index")
  return vector_store