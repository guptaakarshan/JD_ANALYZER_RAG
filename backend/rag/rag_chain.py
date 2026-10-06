from pathlib import Path
from rag.retriever import retrieve_documents_with_stats, MIN_COSINE_SIMILARITY
from rag.llm import llm
from rag.session_store import get_session_paths

from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

prompt_template = PromptTemplate(
    input_variables=["resume_context", "jd_context", "question"],
    template="""
You are an expert Resume and Job Description Analyzer.

Your task is to answer the user's question strictly using the provided Resume Context and Job Description Context.

Instructions:
- Answer only from the provided context.
- Do not make unsupported assumptions or use outside knowledge.
- Keep answers concise and relevant.
- Cite supporting evidence using the source labels provided in the context, for example [resume-1] or [jd-1].
- Do not invent citations.
- If the information is not available in the context, respond exactly with:
  "I couldn't find enough relevant information in the uploaded documents to answer this reliably."

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


def _format_context(docs, doc_type, default_filename):
    context_parts = []
    sources = []

    for idx, (doc, score) in enumerate(docs, start=1):
        label = f"{doc_type}-{idx}"
        metadata = doc.metadata or {}
        raw_source = str(metadata.get("source", default_filename))
        filename = Path(raw_source).name if raw_source else default_filename
        page = metadata.get("page")
        page_num = page + 1 if isinstance(page, int) else (1 if doc_type == "jd" else None)
        snippet = doc.page_content.strip()

        context_parts.append(f"[{label}]\n{snippet}")
        sources.append({
            "label": label,
            "document_type": doc_type,
            "filename": filename,
            "page": page_num,
            "score": round(float(score), 4),
            "snippet": snippet[:300] + ("..." if len(snippet) > 300 else ""),
        })

    return "\n\n".join(context_parts), sources


def generate_answer(query, session_id):
    resume_index_path, jd_index_path, _ = get_session_paths(session_id)

    resume_docs, resume_stats = retrieve_documents_with_stats(
        query,
        str(resume_index_path)
    )

    jd_docs, jd_stats = retrieve_documents_with_stats(
        query,
        str(jd_index_path)
    )

    total_retrieved = resume_stats["retrieved"] + jd_stats["retrieved"]
    total_accepted = resume_stats["accepted"] + jd_stats["accepted"]
    total_rejected = resume_stats["rejected"] + jd_stats["rejected"]

    retrieval_stats = {
        "retrieved": total_retrieved,
        "accepted": total_accepted,
        "rejected": total_rejected,
        "threshold": MIN_COSINE_SIMILARITY,
    }

    # Quality Gate: Weak / Empty retrieval handling
    if not resume_docs and not jd_docs:
        return {
            "answer": "I couldn't find enough relevant information in the uploaded documents to answer this reliably.",
            "sources": [],
            "retrieval_stats": retrieval_stats,
        }

    resume_context, resume_sources = _format_context(resume_docs, "resume", "resume.pdf")
    jd_context, jd_sources = _format_context(jd_docs, "jd", "job_description.txt")

    print("\n===== RESUME CONTEXT =====\n")
    print(resume_context)

    print("\n===== JD CONTEXT =====\n")
    print(jd_context)

    response = chain.invoke({
        "resume_context": resume_context or "No relevant resume sections found.",
        "jd_context": jd_context or "No relevant job description sections found.",
        "question": query,
    })

    return {
        "answer": response,
        "sources": resume_sources + jd_sources,
        "retrieval_stats": retrieval_stats,
    }