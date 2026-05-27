from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv
load_dotenv()

embedding_model=OpenAIEmbeddings(
  model="text-embedding-3-small"
)


def create_embeddings(chunked_documents):
  
  texts=[]
  
  for chunk in chunked_documents:
    texts.append(chunk.page_content)
  
  embeddings=embedding_model.embed_documents(texts)
  return embeddings

