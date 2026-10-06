from langchain_community.vectorstores import FAISS
from langchain_community.vectorstores.utils import DistanceStrategy
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv

load_dotenv()

embedding_model=OpenAIEmbeddings(
  model="text-embedding-3-small"
)

# Cosine similarity is the dot product of unit-normalized embeddings.
FAISS_DISTANCE_STRATEGY = DistanceStrategy.MAX_INNER_PRODUCT
NORMALIZE_EMBEDDINGS = True

def create_vector_store(
  chunked_documents,
  index_path
):

      vector_store=FAISS.from_documents(
       documents = chunked_documents,
        embedding = embedding_model,
        normalize_L2=NORMALIZE_EMBEDDINGS,
        distance_strategy=FAISS_DISTANCE_STRATEGY,
  )
      
      vector_store.save_local(index_path)
      
      return vector_store