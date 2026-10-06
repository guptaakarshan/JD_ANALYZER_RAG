from langchain_community.vectorstores import FAISS
from langchain_community.vectorstores.utils import DistanceStrategy
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv
import os

load_dotenv()

from rag.vectorstore import (
    embedding_model,
    FAISS_DISTANCE_STRATEGY,
    NORMALIZE_EMBEDDINGS,
)
import os

MIN_COSINE_SIMILARITY = float(os.getenv("RETRIEVAL_MIN_COSINE_SIMILARITY", "0.35"))


def load_vector_store(index_path):
  
    vector_store = FAISS.load_local(
        index_path,
        embedding_model,
        allow_dangerous_deserialization=True,
        normalize_L2=NORMALIZE_EMBEDDINGS,
        distance_strategy=FAISS_DISTANCE_STRATEGY,
    )

    return vector_store


def retrieve_documents(
    query,
    index_path,
    k=3,
    min_score=MIN_COSINE_SIMILARITY,
):

    vector_store = load_vector_store(
        index_path
    )

    results = vector_store.similarity_search_with_score(
        query=query,
        k=k
    )

    return [
        (document, float(score))
        for document, score in results
        if float(score) >= min_score
    ]


def retrieve_documents_with_stats(
    query,
    index_path,
    k=3,
    min_score=MIN_COSINE_SIMILARITY,
):
    vector_store = load_vector_store(
        index_path
    )

    results = vector_store.similarity_search_with_score(
        query=query,
        k=k
    )

    accepted = [
        (document, float(score))
        for document, score in results
        if float(score) >= min_score
    ]
    total_retrieved = len(results)
    rejected = total_retrieved - len(accepted)

    return accepted, {
        "retrieved": total_retrieved,
        "accepted": len(accepted),
        "rejected": rejected,
        "threshold": min_score,
    }