from rag.retriever import retrieve_documents
from rag.llm import llm

from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

prompt_template = PromptTemplate(
    input_variables=["resume_context", "jd_context", "question"],
    template="""
You are an expert Resume and Job Description Analyzer.

Your task is to answer the user's question strictly using the provided Resume Context and Job Description Context.

Instructions:
- Answer only from the provided context.
- Do not use outside knowledge.
- Keep answers concise and relevant.
- Use bullet points when listing skills, qualifications, responsibilities, or requirements.
- If the answer requires comparison, provide a clear comparison.
- If the information is not available in the context, respond exactly with:
  "I could not find that information."
- Do not speculate or infer information that is not explicitly stated.

Resume Context:
{resume_context}

Job Description Context:
{jd_context}

Question:
{question}

Answer:
"""
)

chain = (
  prompt_template | llm | StrOutputParser()
)

def generate_answer(query):

    resume_docs = retrieve_documents(
    query,
    "resume_faiss_index"
)

    jd_docs = retrieve_documents(
    query,
    "jd_faiss_index"
)

    resume_context = "\n\n".join(
        [doc.page_content for doc, score in resume_docs]
    )
    
    jd_context = "\n\n".join(
        [doc.page_content for doc, score in jd_docs]
    )
    
    
    print("\n===== RESUME CONTEXT =====\n")
    print(resume_context)

    print("\n===== JD CONTEXT =====\n")
    print(jd_context)

    response = chain.invoke({
        "resume_context": resume_context,
        "jd_context": jd_context,
        "question": query
    })

    return response