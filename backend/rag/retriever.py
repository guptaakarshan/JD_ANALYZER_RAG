from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv

load_dotenv()

# Embedding model used during retrieval
embedding_model = OpenAIEmbeddings(
    model="text-embedding-3-small"
)


def load_vector_store(index_path):
  
    vector_store = FAISS.load_local(
        index_path,
        embedding_model,
        allow_dangerous_deserialization=True
    )

    return vector_store


def retrieve_documents(
    query,
    index_path,
    k=3
):

    vector_store = load_vector_store(
        index_path
    )

    results = vector_store.similarity_search_with_score(
        query=query,
        k=k
    )

    return results