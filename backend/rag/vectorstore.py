from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv

load_dotenv()

embedding_model=OpenAIEmbeddings(
  model="text-embedding-3-small"
)

def create_vector_store(
  chunked_documents,
  index_path
):

      vector_store=FAISS.from_documents(
       documents = chunked_documents,
       embedding = embedding_model
  )
      
      vector_store.save_local(index_path)
      
      return vector_store