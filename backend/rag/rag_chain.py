from rag.retriever import retrieve_documents
from rag.llm import llm

from langchain_core.prompts import PromptTemplate

prompt_template = PromptTemplate(
    input_variables=["context", "question"],
    template="""
You are an expert resume analyzer.

Use ONLY the provided context to answer the question.

If the answer is not present in the context, respond with:
"I could not find that information in the resume."

Context:
{context}

Question:
{question}

Answer:
"""
)

def generate_answer(query):

    documents = retrieve_documents(query)

    context = "\n\n".join(
        [doc.page_content for doc, score in documents]
    )

    final_prompt = prompt_template.format(
        context=context,
        question=query
    )

    response = llm.invoke(final_prompt)

    return response.content