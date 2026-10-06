from rag.retriever import retrieve_documents
from rag.llm import llm
from rag.session_store import get_session_paths

from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from rag.retriever import MIN_COSINE_SIMILARITY
from pathlib import Path

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
- Cite supporting evidence inline using the labels provided in the context, for example [resume-1] or [jd-1].

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

def generate_answer(query, session_id):
    resume_index_path, jd_index_path, _ = get_session_paths(session_id)

    resume_docs = retrieve_documents(
        query,
        str(resume_index_path)
    )

    jd_docs = retrieve_documents(
        query,
        str(jd_index_path)
    )

    resume_context, resume_sources = _format_context(resume_docs, "resume")
    jd_context, jd_sources = _format_context(jd_docs, "jd")

    response = chain.invoke({
        "resume_context": resume_context,
        "jd_context": jd_context,
        "question": query
    })

    return {
        "answer": response,
        "sources": resume_sources + jd_sources,
        "retrieval": {
            "min_cosine_similarity": MIN_COSINE_SIMILARITY,
            "resume_matches": len(resume_sources),
            "jd_matches": len(jd_sources),
        },
    }


def _format_context(results, source_type):
    context_parts = []
    sources = []

    for position, (document, score) in enumerate(results, start=1):
        source_id = f"{source_type}-{position}"
        metadata = document.metadata or {}
        page = metadata.get("page")
        source_name = Path(str(metadata.get("source", source_type))).name
        section = metadata.get("section")
        page_label = f", page {page + 1}" if isinstance(page, int) else ""
        section_label = f", section {section}" if section else ""
        snippet = document.page_content.strip()

        context_parts.append(f"[{source_id}] {snippet}")
        sources.append({
            "id": source_id,
            "type": source_type,
            "source": source_name,
            "page": page + 1 if isinstance(page, int) else None,
            "score": round(float(score), 4),
            "snippet": snippet[:300],
            "section": section,
            "reference": f"{source_name}{page_label}{section_label}",
        })

    return "\n\n".join(context_parts), sources