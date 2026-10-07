import re

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

DEFAULT_CHUNK_SIZE = 500
DEFAULT_CHUNK_OVERLAP = 50
SECTION_CHUNK_SIZE = 700
SECTION_CHUNK_OVERLAP = 100

RESUME_HEADINGS = {
  "summary": re.compile(r"^(?:(?:professional|executive|career|personal)?\s*summary(?:\s+of\s+qualifications)?|(?:career\s+)?objective|about\s+me|(?:professional\s+)?profile)\s*:?$", re.IGNORECASE),
  "achievements_certifications": re.compile(r"^(?:(?:achievements?|awards?|honors?)\s*(?:and|&)\s*(?:certifications?|certificates?)|(?:certifications?|certificates?)\s*(?:and|&)\s*(?:achievements?|awards?|honors?))\s*:?$", re.IGNORECASE),
  "skills": re.compile(r"^(?:(?:technical|core|key|professional|relevant|it|computer)?\s*skills(?:\s*(?:and|&)\s*(?:technologies|tools|competencies))?|(?:technical\s+)?(?:proficiencies|competencies)|(?:technologies\s*(?:and|&)\s*tools)|tech(?:nical)?\s+stack|areas\s+of\s+expertise)\s*:?$", re.IGNORECASE),
  "experience": re.compile(r"^(?:(?:work|professional|relevant|employment|career|industry)\s+)?(?:experience|history)\s*:?$", re.IGNORECASE),
  "projects": re.compile(r"^(?:(?:personal|academic|key|technical|selected|notable|featured)\s+)?projects?\s*:?$", re.IGNORECASE),
  "education": re.compile(r"^(?:education(?:\s*(?:and|&)\s*(?:credentials|qualifications))?|academic\s+(?:background|history|qualifications|credentials)|educational\s+(?:background|qualifications)|academics)\s*:?$", re.IGNORECASE),
  "achievements": re.compile(r"^(?:(?:key|major|personal)?\s*)?(?:achievements?|accomplishments?|awards?|honors?(?:\s*(?:and|&)\s*awards?)?)\s*:?$", re.IGNORECASE),
  "certifications": re.compile(r"^(?:(?:professional|licenses?\s*(?:and|&)\s*)?certifications?|certificates?|licenses?)\s*:?$", re.IGNORECASE),
}

JD_HEADINGS = {
  "about_the_role": re.compile(r"^(?:about\s+(?:the\s+)?(?:role|job|position|company|organization|team|us)|(?:role|job|position)\s+(?:overview|summary|description)|company\s+overview)\s*:?$", re.IGNORECASE),
  "what_you_will_do": re.compile(r"^(?:what\s+you(?:'|’)?ll\s+(?:do|be\s+doing|bring)|what\s+you\s+will\s+(?:do|be\s+doing|bring))\s*:?$", re.IGNORECASE),
  "responsibilities": re.compile(r"^(?:(?:key|core|role|primary|essential)?\s*responsibilities|roles?\s+and\s+responsibilities|duties|job\s+duties)\s*:?$", re.IGNORECASE),
  "required_qualifications": re.compile(r"^(?:(?:required|minimum|basic|mandatory|must[\s\-]*have)\s+qualifications?)\s*:?$", re.IGNORECASE),
  "preferred_qualifications": re.compile(r"^(?:(?:preferred|desired|bonus|nice[\s\-]*to[\s\-]*have|additional)\s+qualifications?)\s*:?$", re.IGNORECASE),
  "qualifications": re.compile(r"^(?:(?:candidate|general)?\s*qualifications?)\s*:?$", re.IGNORECASE),
  "preferred_skills": re.compile(r"^(?:(?:preferred|desired|bonus|nice[\s\-]*to[\s\-]*have)\s+(?:skills|technologies|competencies))(?:\s*(?:and|&)\s*technologies)?\s*:?$", re.IGNORECASE),
  "requirements": re.compile(r"^(?:(?:key|minimum|basic|role|job|core|primary)?\s*requirements?)\s*:?$", re.IGNORECASE),
  "skills": re.compile(r"^(?:(?:required|technical|core|key)\s+)?skills(?:\s*(?:and|&)\s*(?:technologies|tools))?\s*:?$", re.IGNORECASE),
  "experience": re.compile(r"^(?:(?:work|professional|required|relevant|industry)?\s*experience(?:\s+required)?)\s*:?$", re.IGNORECASE),
  "what_we_offer": re.compile(r"^(?:what\s+we\s+(?:offer|provide)|we\s+offer|(?:perks\s*(?:and|&)\s*benefits|benefits\s*(?:and|&)\s*perks|benefits|perks)|why\s+join\s+us)\s*:?$", re.IGNORECASE),
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
  active_heading = None

  for document in documents:
    current_lines = []

    for line in document.page_content.splitlines():
      heading = _match_heading(line, headings)
      if heading:
        if active_heading is not None and current_lines:
          sectioned_documents.append(
            _section_document(document, active_heading, current_lines)
          )
          current_lines = [line]
        else:
          current_lines.append(line)
        active_heading = heading
      else:
        current_lines.append(line)

    if current_lines:
      sectioned_documents.append(
        _section_document(document, active_heading or "general", current_lines)
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
  items = headings.items() if isinstance(headings, dict) else headings
  for heading, pattern in items:
    if pattern.match(normalized_line):
      return heading
  return None


def _section_document(document, section, lines):
  metadata = dict(document.metadata)
  if section and section != "general":
    metadata["section"] = section
  return Document(
    page_content="\n".join(lines).strip(),
    metadata=metadata,
  )
 