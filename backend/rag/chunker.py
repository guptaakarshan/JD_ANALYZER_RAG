import re

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

DEFAULT_CHUNK_SIZE = 500
DEFAULT_CHUNK_OVERLAP = 50
SECTION_CHUNK_SIZE = 700
SECTION_CHUNK_OVERLAP = 100

RESUME_HEADINGS = {
  "skills": re.compile(r"^(?:(?:technical|core|key)\s+)?skills(?:\s*(?:and|&)\s*technologies)?\s*:?[\s|\-]*$", re.IGNORECASE),
  "experience": re.compile(r"^(?:(?:work|professional|relevant|employment)\s+)?(?:experience|history)\s*:?[\s|\-]*$", re.IGNORECASE),
  "education": re.compile(r"^(?:education|academic\s+(?:background|history)|educational\s+background)\s*:?[\s|\-]*$", re.IGNORECASE),
  "projects": re.compile(r"^(?:(?:personal|academic|key)\s+)?projects?\s*:?[\s|\-]*$", re.IGNORECASE),
}

JD_HEADINGS = {
  "responsibilities": re.compile(r"^(?:(?:key|core|role)?\s*responsibilities|roles?\s+and\s+responsibilities|duties)\s*:?[\s|\-]*$", re.IGNORECASE),
  "requirements": re.compile(r"^(?:(?:key|minimum|basic|role)?\s*requirements?)\s*:?[\s|\-]*$", re.IGNORECASE),
  "qualifications": re.compile(r"^(?:(?:minimum|basic|preferred)?\s*qualifications?)\s*:?[\s|\-]*$", re.IGNORECASE),
  "skills": re.compile(r"^(?:(?:required|preferred|technical|core)\s+)?skills(?:\s*(?:and|&)\s*technologies)?\s*:?[\s|\-]*$", re.IGNORECASE),
  "what you will do": re.compile(r"^(?:what\s+you(?:'|’)?ll\s+(?:do|be\s+doing)|what\s+you\s+will\s+(?:do|be\s+doing)|what\s+you(?:'|’)?ll\s+bring)\s*:?[\s|\-]*$", re.IGNORECASE),
}


def split_documents(documents, document_type="resume"):
  headings = RESUME_HEADINGS if document_type == "resume" else JD_HEADINGS
  sectioned_documents = _split_by_sections(documents, headings)

  if not sectioned_documents:
    return _recursive_split(documents, DEFAULT_CHUNK_SIZE, DEFAULT_CHUNK_OVERLAP)

  section_splitter = RecursiveCharacterTextSplitter(
    chunk_size=SECTION_CHUNK_SIZE,
    chunk_overlap=SECTION_CHUNK_OVERLAP,
  )
  return section_splitter.split_documents(sectioned_documents)


def _recursive_split(documents, chunk_size, chunk_overlap):
  text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=chunk_size,
    chunk_overlap=chunk_overlap,
  )
  return text_splitter.split_documents(documents)


def _split_by_sections(documents, headings):
  sectioned_documents = []

  for document in documents:
    current_heading = "general"
    current_lines = []

    for line in document.page_content.splitlines():
      heading = _match_heading(line, headings)
      if heading:
        if current_lines:
          sectioned_documents.append(
            _section_document(document, current_heading, current_lines)
          )
        current_heading = heading
        current_lines = [line]
      else:
        current_lines.append(line)

    if current_lines:
      sectioned_documents.append(
        _section_document(document, current_heading, current_lines)
      )

  detected_sections = [
    doc for doc in sectioned_documents
    if doc.metadata.get("section") and doc.metadata.get("section") != "general"
  ]
  return sectioned_documents if detected_sections else []


def _match_heading(line, headings):
  cleaned = re.sub(r"^[#*\-\s]+", "", line.strip())
  cleaned = re.sub(r"[*:\s]+$", "", cleaned).strip()
  normalized_line = re.sub(r"\s+", " ", cleaned)
  for heading, pattern in headings.items():
    if pattern.match(normalized_line):
      return heading
  return None


def _section_document(document, section, lines):
  metadata = dict(document.metadata)
  if section != "general":
    metadata["section"] = section
  return Document(
    page_content="\n".join(lines).strip(),
    metadata=metadata,
  )
 