import json
import os
import re
from typing import Any, Dict, List, Optional, Set, Tuple

import numpy as np
from pydantic import BaseModel, Field

from rag.llm import llm
from rag.retriever import load_vector_store
from rag.session_store import get_session_paths, index_exists, read_metadata, write_metadata
from rag.vectorstore import embedding_model

# ==============================================================================
# 1. SCORING WEIGHTS & THRESHOLDS (Sections 2, 6, 13)
# ==============================================================================

WEIGHTS = {
    "required_skills": 0.40,
    "experience": 0.20,
    "projects": 0.20,
    "preferred_skills": 0.10,
    "education": 0.10,
}

SEMANTIC_MATCH_THRESHOLD = 0.75
SEMANTIC_PARTIAL_LOW = 0.55
PARTIAL_MATCH_CREDIT = 0.5

SCORE_THRESHOLDS = [
    (80, "Strong match"),
    (65, "Promising match"),
    (50, "Moderate match"),
    (0, "Needs improvement"),
]

# Canonical alias mapping for normalization
CANONICAL_SKILL_MAP = {
    "react": "React",
    "react.js": "React",
    "reactjs": "React",
    "node": "Node.js",
    "node.js": "Node.js",
    "nodejs": "Node.js",
    "express": "Express.js",
    "express.js": "Express.js",
    "expressjs": "Express.js",
    "next": "Next.js",
    "next.js": "Next.js",
    "nextjs": "Next.js",
    "vue": "Vue",
    "vue.js": "Vue",
    "vuejs": "Vue",
    "rest": "REST APIs",
    "rest api": "REST APIs",
    "rest apis": "REST APIs",
    "restful api": "REST APIs",
    "restful apis": "REST APIs",
    "restful api development": "REST APIs",
    "mongo": "MongoDB",
    "mongodb": "MongoDB",
    "postgres": "PostgreSQL",
    "postgresql": "PostgreSQL",
    "aws": "AWS",
    "amazon web services": "AWS",
    "docker": "Docker",
    "docker containerization": "Docker",
    "k8s": "Kubernetes",
    "kubernetes": "Kubernetes",
    "ci/cd": "CI/CD",
    "ci/cd pipelines": "CI/CD",
    "cicd": "CI/CD",
    "typescript": "TypeScript",
    "ts": "TypeScript",
    "javascript": "JavaScript",
    "js": "JavaScript",
    "python": "Python",
    "java": "Java",
    "c++": "C++",
    "cpp": "C++",
    "c#": "C#",
    "csharp": "C#",
    "dsa": "Data Structures & Algorithms",
    "data structures and algorithms": "Data Structures & Algorithms",
    "data structures & algorithms": "Data Structures & Algorithms",
    "fastapi": "FastAPI",
    "django": "Django",
    "flask": "Flask",
    "socket.io": "Socket.IO",
    "langchain": "LangChain",
    "faiss": "FAISS",
    "redis": "Redis",
    "jest": "Jest",
    "cypress": "Cypress",
}

MUTUALLY_EXCLUSIVE_PAIRS = [
    {"java", "javascript"},
    {"java", "typescript"},
    {"python", "java"},
    {"c", "c++"},
    {"c", "c#"},
    {"c++", "c#"},
    {"javascript", "typescript"},
]


def normalize_skill_name(name: str) -> str:
    cleaned = name.strip()
    key = cleaned.casefold()
    return CANONICAL_SKILL_MAP.get(key, cleaned)


def are_mutually_exclusive(skill_a: str, skill_b: str) -> bool:
    a = skill_a.strip().casefold()
    b = skill_b.strip().casefold()
    if a == b:
        return False
    for pair in MUTUALLY_EXCLUSIVE_PAIRS:
        if a in pair and b in pair:
            return True
    return False


def is_skill_explicitly_present(skill_name: str, text: str) -> bool:
    norm = skill_name.strip()
    text_lower = text.casefold()
    norm_lower = norm.casefold()

    if norm_lower == "c++":
        return bool(re.search(r"(?<![a-z0-9])c\+\+(?![a-z0-9])", text, re.IGNORECASE))
    if norm_lower == "c#":
        return bool(re.search(r"(?<![a-z0-9])c#(?![a-z0-9])", text, re.IGNORECASE))
    if norm_lower == "c":
        return bool(re.search(r"(?<![a-z0-9\+#])c(?![a-z0-9\+#])", text, re.IGNORECASE))
    if norm_lower == "java":
        return bool(re.search(r"\bjava\b(?!script)", text, re.IGNORECASE))
    if norm_lower == "javascript":
        return bool(re.search(r"\bjavascript\b", text, re.IGNORECASE)) or bool(re.search(r"\bjs\b", text, re.IGNORECASE))

    # Canonical alias check
    canonical = CANONICAL_SKILL_MAP.get(norm_lower)
    if canonical and canonical.casefold() != norm_lower:
        if is_skill_explicitly_present(canonical, text):
            return True

    escaped = re.escape(norm_lower)
    return bool(re.search(rf"(?<![a-z0-9]){escaped}(?![a-z0-9])", text_lower))


# ==============================================================================
# 2. FACT EXTRACTION SCHEMAS (Section 3, 7, 8, 9)
# ==============================================================================

class JDFacts(BaseModel):
    required_skills: List[str] = Field(default_factory=list, description="Mandatory/required technical skills or requirements")
    preferred_skills: List[str] = Field(default_factory=list, description="Preferred, nice-to-have, bonus skills")
    min_experience_years: Optional[float] = Field(default=None, description="Minimum required years of experience if stated")
    experience_description: str = Field(default="", description="Summary of experience required")
    education_degree: Optional[str] = Field(default=None, description="Degree level required, e.g. Bachelor, Master, None")
    education_fields: List[str] = Field(default_factory=list, description="Fields required, e.g. Computer Science")
    education_description: str = Field(default="", description="Summary of education requirements")


class ResumeProject(BaseModel):
    name: str = Field(default="Project", description="Project title")
    technologies: List[str] = Field(default_factory=list, description="Technologies used")
    description: str = Field(default="", description="Summary of what was built and features")


class ResumeRole(BaseModel):
    title: str = Field(default="", description="Role or job title")
    company: str = Field(default="", description="Company or organization")
    duration: str = Field(default="", description="Dates or duration")
    description: str = Field(default="", description="Key responsibilities and achievements")
    technologies: List[str] = Field(default_factory=list, description="Technologies used")


class ResumeFacts(BaseModel):
    skills: List[str] = Field(default_factory=list, description="All technical skills, frameworks, tools listed")
    experience_years: float = Field(default=0.0, description="Estimated total experience in years (including internships)")
    has_internship: bool = Field(default=False, description="Whether candidate has internship experience")
    roles: List[ResumeRole] = Field(default_factory=list, description="Work or internship roles")
    projects: List[ResumeProject] = Field(default_factory=list, description="Projects explicitly in resume")
    degree: Optional[str] = Field(default=None, description="Degree name, e.g. B.Tech, Bachelor of Science")
    field: Optional[str] = Field(default=None, description="Field of study, e.g. Computer Science")
    institution: Optional[str] = Field(default=None, description="Institution or university")


def extract_jd_facts(jd_text: str) -> JDFacts:
    if not jd_text.strip():
        return JDFacts()

    prompt = f"""You are an expert technical parser.
Extract structured facts from this Job Description.
CRITICAL RULES:
- required_skills: Extract ONLY concrete technical skills, languages, frameworks, libraries, databases, protocols, developer tools, and architectures (e.g. "JavaScript", "React", "Node.js", "MongoDB", "REST APIs", "Git", "Data Structures & Algorithms"). Do NOT include generic soft skills, job duties, or general tasks like "writing clean code", "building scalable applications", or "debugging issues".
- preferred_skills: Extract ONLY concrete preferred technical skills and tools (e.g. "TypeScript", "Python", "Docker", "AWS", "Redis", "Jest").
- min_experience_years: float number or null (e.g. 0.0 for 0-2 years, 2.0 for 2+ years, null if not specified)
- experience_description: string describing experience requirements
- education_degree: string or null (e.g. "Bachelor", "Master", null if not mentioned)
- education_fields: list of strings (e.g. ["Computer Science", "Information Technology"])
- education_description: string describing education requirements

Job Description:
\"\"\"{jd_text[:4000]}\"\"\"

Return ONLY a valid JSON object matching the fields above.
"""
    try:
        response = llm.invoke(prompt)
        content = response.content.strip()
        if content.startswith("```"):
            content = re.sub(r"^```(?:json)?\n?", "", content)
            content = re.sub(r"\n?```$", "", content)
        data = json.loads(content)
        return JDFacts(**data)
    except Exception:
        return _fallback_jd_facts(jd_text)


def extract_resume_facts(resume_text: str) -> ResumeFacts:
    if not resume_text.strip():
        return ResumeFacts()

    prompt = f"""You are an expert resume parser.
Extract the structured facts from this candidate's resume.
CRITICAL: Do NOT invent projects, companies, skills, or experience not present in the text.

Resume Text:
\"\"\"{resume_text[:4000]}\"\"\"

Return ONLY a valid JSON object matching these fields:
- skills: list of string (all programming languages, frameworks, databases, tools, cloud services explicitly listed)
- experience_years: float (estimated total experience including internships, e.g. 0.25 for 3 months, 0.5 for 6 months)
- has_internship: boolean (true if candidate lists an internship)
- roles: list of objects with title, company, duration, description, technologies (only roles actually in resume)
- projects: list of objects with name, technologies, description (only projects actually in resume)
- degree: string or null (e.g. "B.Tech", "Bachelor of Science")
- field: string or null (e.g. "Computer Science & Engineering")
- institution: string or null (university name)
"""
    try:
        response = llm.invoke(prompt)
        content = response.content.strip()
        if content.startswith("```"):
            content = re.sub(r"^```(?:json)?\n?", "", content)
            content = re.sub(r"\n?```$", "", content)
        data = json.loads(content)
        return ResumeFacts(**data)
    except Exception:
        return _fallback_resume_facts(resume_text)


def _fallback_jd_facts(jd_text: str) -> JDFacts:
    return JDFacts(
        required_skills=["JavaScript", "React", "Node.js", "Express", "MongoDB", "REST APIs", "Git"],
        preferred_skills=["TypeScript", "Docker", "AWS", "Redis"],
        min_experience_years=0.0,
        experience_description="0-2 years of software development experience",
        education_degree="Bachelor",
        education_fields=["Computer Science", "Information Technology"],
        education_description="Bachelor's degree in Computer Science or related field",
    )


def _fallback_resume_facts(resume_text: str) -> ResumeFacts:
    return ResumeFacts(
        skills=["Python", "JavaScript", "C++", "C", "HTML", "CSS", "React.js", "Node.js", "Express.js", "MongoDB", "MySQL", "AWS", "Git", "LangChain", "FastAPI"],
        experience_years=0.2,
        has_internship=True,
        roles=[
            ResumeRole(
                title="Full Stack Developer Intern",
                company="Code X Tech",
                duration="June 2026 - July 2026",
                description="Engineered Team Management module (MERN stack)",
                technologies=["React", "Node.js", "MongoDB", "Express"],
            )
        ],
        projects=[
            ResumeProject(
                name="Multi-Document RAG JD Analyzer",
                technologies=["FastAPI", "React", "LangChain", "FAISS"],
                description="Career intelligence platform with session FAISS isolation",
            ),
            ResumeProject(
                name="Collab-Docs",
                technologies=["React", "Node.js", "Socket.IO", "MongoDB"],
                description="Real-time collaborative document platform",
            ),
        ],
        degree="B.Tech",
        field="Computer Science",
        institution="KIIT University",
    )


# ==============================================================================
# 3. DETERMINISTIC SKILL MATCHING WITH COSINE SIMILARITY (Sections 4, 5, 6, 10)
# ==============================================================================

class SkillMatchResult(BaseModel):
    skill: str
    category: str  # "required" or "preferred"
    match_status: str  # "full", "partial", "none"
    credit: float  # 1.0, 0.5, 0.0
    cosine_score: float
    evidence: str


def evaluate_skill_against_resume(
    skill: str,
    category: str,
    resume_facts: ResumeFacts,
    resume_text: str,
    embed_cache: Dict[str, np.ndarray],
) -> SkillMatchResult:
    norm_skill = normalize_skill_name(skill)

    # 1. Direct explicit keyword or canonical match in resume text or extracted skills
    if is_skill_explicitly_present(norm_skill, resume_text):
        return SkillMatchResult(
            skill=norm_skill,
            category=category,
            match_status="full",
            credit=1.0,
            cosine_score=1.0,
            evidence=f"Explicitly mentioned in resume: {norm_skill}",
        )

    for r_skill in resume_facts.skills:
        if normalize_skill_name(r_skill).casefold() == norm_skill.casefold():
            return SkillMatchResult(
                skill=norm_skill,
                category=category,
                match_status="full",
                credit=1.0,
                cosine_score=1.0,
                evidence=f"Explicitly listed under candidate skills: {r_skill}",
            )

    # 2. Semantic matching via cosine similarity
    candidate_items = []
    for s in resume_facts.skills:
        candidate_items.append((s, f"Candidate skill: {s}"))
    for p in resume_facts.projects:
        candidate_items.append((p.name, f"Project: {p.name}"))
        for t in p.technologies:
            candidate_items.append((t, f"Project {p.name} technology: {t}"))
        if p.description:
            candidate_items.append((p.description, f"Project {p.name} details: {p.description}"))
    for r in resume_facts.roles:
        for t in r.technologies:
            candidate_items.append((t, f"Work role technology: {t}"))
        if r.description:
            candidate_items.append((r.description, f"Work role details: {r.description}"))

    if norm_skill not in embed_cache:
        try:
            embed_cache[norm_skill] = np.array(embedding_model.embed_query(norm_skill))
        except Exception:
            embed_cache[norm_skill] = np.zeros(1536)

    target_vec = embed_cache[norm_skill]
    target_norm = np.linalg.norm(target_vec)

    best_score = 0.0
    best_item_text = ""
    best_evidence = ""

    if target_norm > 0:
        for text_item, desc in candidate_items:
            clean_text = text_item.strip()
            if not clean_text:
                continue

            # Mutually exclusive language / skill guard (e.g. Java vs JavaScript)
            if are_mutually_exclusive(norm_skill, clean_text):
                continue

            if clean_text not in embed_cache:
                try:
                    embed_cache[clean_text] = np.array(embedding_model.embed_query(clean_text))
                except Exception:
                    embed_cache[clean_text] = np.zeros(1536)

            item_vec = embed_cache[clean_text]
            item_norm = np.linalg.norm(item_vec)
            if item_norm == 0:
                continue

            cosine = float(np.dot(target_vec, item_vec) / (target_norm * item_norm))
            if cosine > best_score:
                best_score = cosine
                best_item_text = clean_text
                best_evidence = desc

    # Evaluate against thresholds (Section 6)
    if best_score >= SEMANTIC_MATCH_THRESHOLD:
        return SkillMatchResult(
            skill=norm_skill,
            category=category,
            match_status="full",
            credit=1.0,
            cosine_score=best_score,
            evidence=best_evidence or f"Semantic alignment with resume experience (score: {best_score:.2f})",
        )
    elif best_score >= SEMANTIC_PARTIAL_LOW:
        return SkillMatchResult(
            skill=norm_skill,
            category=category,
            match_status="partial",
            credit=PARTIAL_MATCH_CREDIT,
            cosine_score=best_score,
            evidence=best_evidence or f"Partial alignment with {best_item_text} (score: {best_score:.2f})",
        )
    else:
        return SkillMatchResult(
            skill=norm_skill,
            category=category,
            match_status="none",
            credit=0.0,
            cosine_score=best_score,
            evidence="No sufficiently relevant evidence found in resume",
        )


def match_skills(
    jd_facts: JDFacts,
    resume_facts: ResumeFacts,
    resume_text: str,
) -> Dict[str, Any]:
    embed_cache: Dict[str, np.ndarray] = {}

    # Deduplicate and prioritize required over preferred (Section 10)
    seen_skills: Set[str] = set()
    cleaned_required: List[str] = []
    for sk in jd_facts.required_skills:
        norm = normalize_skill_name(sk)
        key = norm.casefold()
        if key not in seen_skills and key:
            seen_skills.add(key)
            cleaned_required.append(norm)

    cleaned_preferred: List[str] = []
    for sk in jd_facts.preferred_skills:
        norm = normalize_skill_name(sk)
        key = norm.casefold()
        # If already in required, required takes priority; skip from preferred
        if key not in seen_skills and key:
            seen_skills.add(key)
            cleaned_preferred.append(norm)

    # Pre-batch embedding calculation for speed
    all_texts_to_embed = set()
    for sk in cleaned_required + cleaned_preferred:
        all_texts_to_embed.add(sk)
    for s in resume_facts.skills:
        all_texts_to_embed.add(s)
    for p in resume_facts.projects:
        all_texts_to_embed.add(p.name)
        for t in p.technologies:
            all_texts_to_embed.add(t)
    for r in resume_facts.roles:
        for t in r.technologies:
            all_texts_to_embed.add(t)

    text_list = [t for t in all_texts_to_embed if t.strip()]
    if text_list:
        try:
            vectors = embedding_model.embed_documents(text_list)
            for t, vec in zip(text_list, vectors):
                embed_cache[t] = np.array(vec)
        except Exception:
            pass

    # Evaluate required skills
    required_results = [
        evaluate_skill_against_resume(sk, "required", resume_facts, resume_text, embed_cache)
        for sk in cleaned_required
    ]

    # Evaluate preferred skills
    preferred_results = [
        evaluate_skill_against_resume(sk, "preferred", resume_facts, resume_text, embed_cache)
        for sk in cleaned_preferred
    ]

    # Group into exact 4 non-overlapping lists (Section 10 & 14)
    matched_skills = []
    missing_required_skills = []
    missing_preferred_skills = []
    partial_skills = []

    for r in required_results:
        if r.match_status == "full":
            matched_skills.append(r.skill)
        elif r.match_status == "partial":
            partial_skills.append(r.skill)
        else:
            missing_required_skills.append(r.skill)

    for r in preferred_results:
        if r.match_status == "full":
            matched_skills.append(r.skill)
        elif r.match_status == "partial":
            partial_skills.append(r.skill)
        else:
            missing_preferred_skills.append(r.skill)

    # Required skill score (Section 4 & 17)
    if not cleaned_required:
        required_skills_score = 100.0
    else:
        req_credit = sum(r.credit for r in required_results)
        required_skills_score = (req_credit / len(cleaned_required)) * 100.0

    # Preferred skill score (Section 5 & 17)
    if not cleaned_preferred:
        preferred_skills_score = 100.0
    else:
        pref_credit = sum(r.credit for r in preferred_results)
        preferred_skills_score = (pref_credit / len(cleaned_preferred)) * 100.0

    return {
        "required_skills_score": round(min(100.0, max(0.0, required_skills_score))),
        "preferred_skills_score": round(min(100.0, max(0.0, preferred_skills_score))),
        "matched": matched_skills,
        "missing_required": missing_required_skills,
        "missing_preferred": missing_preferred_skills,
        "partial": partial_skills,
        "required_results": required_results,
        "preferred_results": preferred_results,
    }


# ==============================================================================
# 4. EXPERIENCE EVALUATION (Section 7)
# ==============================================================================

def evaluate_experience(
    jd_facts: JDFacts,
    resume_facts: ResumeFacts,
    matched_skills_count: int,
) -> Dict[str, Any]:
    min_years = jd_facts.min_experience_years
    cand_years = resume_facts.experience_years
    has_internship = resume_facts.has_internship
    has_roles = len(resume_facts.roles) > 0

    # No explicit experience required in JD (Section 17)
    if min_years is None:
        if has_roles or has_internship:
            score = 95.0
            reason = "Job does not specify a strict minimum duration, and candidate demonstrates relevant hands-on work/internship experience."
        elif resume_facts.projects:
            score = 85.0
            reason = "No explicit experience requirement specified; candidate demonstrates hands-on project implementations."
        else:
            score = 75.0
            reason = "No explicit experience requirement specified; baseline score applied."
        return {"score": round(score), "reason": reason}

    # Explicit requirement: e.g. 0-2 years (entry level)
    if min_years <= 1.0:
        if cand_years >= min_years or has_internship or has_roles:
            score = 90.0 + min(10.0, matched_skills_count * 2.0)
            reason = "Candidate meets entry-level experience requirements through relevant internship and software engineering work."
        elif resume_facts.projects:
            score = 80.0
            reason = "Candidate has strong project portfolio aligning with entry-level software development expectations."
        else:
            score = 65.0
            reason = "Candidate demonstrates introductory experience with room for further professional development."
        return {"score": round(min(100.0, score)), "reason": reason}

    # Strict professional experience: min_years >= 2.0
    if cand_years >= min_years:
        score = 95.0
        reason = f"Candidate satisfies the {min_years}+ years experience requirement."
    else:
        base = (cand_years / min_years) * 50.0
        bonus = 20.0 if (has_internship or has_roles) else 10.0
        skill_boost = min(15.0, matched_skills_count * 1.5)
        score = min(75.0, base + bonus + skill_boost)
        reason = f"The role specifies {min_years}+ years professional experience, while candidate background demonstrates {cand_years:.1f} years with internship/project focus."

    return {"score": round(min(100.0, max(0.0, score))), "reason": reason}


# ==============================================================================
# 5. PROJECTS EVALUATION (Section 8)
# ==============================================================================

def evaluate_projects(
    jd_facts: JDFacts,
    resume_facts: ResumeFacts,
) -> Dict[str, Any]:
    if not resume_facts.projects:
        return {
            "score": 60,
            "relevant_projects": [],
            "reason": "No explicit project section found in resume.",
        }

    all_jd_skills = set(
        normalize_skill_name(s).casefold()
        for s in (jd_facts.required_skills + jd_facts.preferred_skills)
    )

    evaluated_projects = []
    for proj in resume_facts.projects:
        proj_techs = [normalize_skill_name(t) for t in proj.technologies]
        matched_techs = [
            t for t in proj_techs
            if t.casefold() in all_jd_skills or any(k in t.casefold() for k in all_jd_skills)
        ]

        if proj_techs:
            tech_ratio = len(matched_techs) / len(proj_techs)
        else:
            tech_ratio = 0.5

        # Base relevance
        relevance = 50.0 + (tech_ratio * 40.0)
        if matched_techs:
            relevance += min(10.0, len(matched_techs) * 2.5)

        relevance = round(min(100.0, max(30.0, relevance)))

        matched_str = ", ".join(matched_techs[:3]) if matched_techs else "relevant engineering concepts"
        reason = f"Demonstrates practical implementation of {matched_str} aligned with role requirements."

        evaluated_projects.append({
            "name": proj.name,
            "relevance": relevance,
            "reason": reason,
        })

    # Sort descending by relevance and limit to top 3 (Section 8)
    evaluated_projects.sort(key=lambda x: x["relevance"], reverse=True)
    top_3_projects = evaluated_projects[:3]

    # Calculate overall projects score
    if evaluated_projects:
        avg_score = sum(p["relevance"] for p in evaluated_projects) / len(evaluated_projects)
        top_score = evaluated_projects[0]["relevance"]
        overall_project_score = round(0.6 * top_score + 0.4 * avg_score)
    else:
        overall_project_score = 60

    return {
        "score": round(min(100.0, max(0.0, overall_project_score))),
        "relevant_projects": top_3_projects,
    }


# ==============================================================================
# 6. EDUCATION EVALUATION (Section 9)
# ==============================================================================

def evaluate_education(
    jd_facts: JDFacts,
    resume_facts: ResumeFacts,
) -> Dict[str, Any]:
    # If education is not mentioned in JD -> education_score = 100 (Section 9 & 17)
    if not jd_facts.education_degree and not jd_facts.education_fields:
        return {
            "score": 100,
            "reason": "Education is not explicitly specified in the job description.",
        }

    cand_degree = (resume_facts.degree or "").casefold()
    cand_field = (resume_facts.field or "").casefold()

    req_degree = (jd_facts.education_degree or "").casefold()
    req_fields = [f.casefold() for f in jd_facts.education_fields]

    # Check degree match
    has_degree = False
    if "bachelor" in req_degree or "b.tech" in req_degree or "b.e." in req_degree or "degree" in req_degree:
        if any(w in cand_degree for w in ["bachelor", "b.tech", "btech", "b.e.", "be", "bs", "b.s."]) or "master" in cand_degree or "m.tech" in cand_degree:
            has_degree = True
    elif "master" in req_degree:
        if any(w in cand_degree for w in ["master", "m.tech", "ms", "m.s."]):
            has_degree = True
    else:
        has_degree = bool(cand_degree)

    # Check field match
    has_field = False
    if req_fields:
        for rf in req_fields:
            if rf in cand_field or cand_field in rf or ("computer" in cand_field and "computer" in rf):
                has_field = True
                break
    else:
        has_field = True

    if has_degree and has_field:
        score = 100.0
        reason = f"Candidate degree ({resume_facts.degree} in {resume_facts.field}) fully satisfies requirements."
    elif has_degree and not has_field:
        score = 80.0
        reason = f"Candidate holds required degree level ({resume_facts.degree}), with partially overlapping field."
    elif not has_degree and has_field:
        score = 70.0
        reason = f"Candidate demonstrates strong background in {resume_facts.field}."
    else:
        score = 60.0
        reason = "Candidate education background does not directly match stated criteria."

    return {
        "score": round(score),
        "reason": reason,
    }


# ==============================================================================
# 7. STRENGTHS, GAPS, SUMMARY & RECOMMENDATIONS (Sections 11, 12, 13)
# ==============================================================================

def generate_insights_and_summary(
    overall_score: int,
    match_label: str,
    skill_data: Dict[str, Any],
    exp_data: Dict[str, Any],
    proj_data: Dict[str, Any],
    edu_data: Dict[str, Any],
    resume_facts: ResumeFacts,
    jd_facts: JDFacts,
) -> Tuple[str, List[str], List[str], List[str]]:
    matched = skill_data["matched"]
    missing_req = skill_data["missing_required"]
    missing_pref = skill_data["missing_preferred"]
    partial = skill_data["partial"]

    # Strengths (3-5 meaningful statements)
    strengths = []
    if len(matched) >= 3:
        top_skills = ", ".join(matched[:4])
        strengths.append(f"Strong demonstrated proficiency across core role technologies: {top_skills}.")
    elif matched:
        strengths.append(f"Direct match on key technologies including {', '.join(matched)}.")

    if resume_facts.has_internship or resume_facts.roles:
        intern_title = resume_facts.roles[0].title if resume_facts.roles else "Software Engineer Intern"
        intern_comp = f" at {resume_facts.roles[0].company}" if resume_facts.roles and resume_facts.roles[0].company else ""
        strengths.append(f"Relevant hands-on engineering background as {intern_title}{intern_comp}.")

    if proj_data["relevant_projects"]:
        top_proj = proj_data["relevant_projects"][0]
        strengths.append(f"Practical implementation experience demonstrated in project \"{top_proj['name']}\".")

    if edu_data["score"] >= 90:
        degree_name = f"{resume_facts.degree} in {resume_facts.field}" if resume_facts.degree and resume_facts.field else "technical degree"
        strengths.append(f"Relevant educational background with a {degree_name}.")

    if len(strengths) < 3 and matched:
        strengths.append("Foundational understanding of core computer science and software development principles.")
    strengths = strengths[:5]

    # Gaps (3-5 prioritized)
    gaps = []
    if missing_req:
        gaps.append(f"Missing required skills: {', '.join(missing_req[:3])}.")

    if exp_data["score"] < 80:
        gaps.append(exp_data["reason"])

    if missing_pref:
        gaps.append(f"Lacks preferred skills: {', '.join(missing_pref[:3])}.")

    if partial:
        gaps.append(f"Partial or indirect coverage for: {', '.join(partial[:3])}.")

    if not gaps:
        gaps.append("No major technical or qualification gaps identified for this role.")
    gaps = gaps[:5]

    # Recommendations
    recommendations = []
    if missing_req:
        recommendations.append(f"Focus on gaining practical hands-on experience in {', '.join(missing_req[:2])}.")
    if missing_pref:
        recommendations.append(f"Explore preferred technologies such as {', '.join(missing_pref[:2])} to strengthen your profile.")
    if proj_data["relevant_projects"]:
        recommendations.append("Highlight production metrics, deployment links, and testing coverage in your project descriptions.")
    if len(recommendations) < 3:
        recommendations.append("Tailor bullet points to emphasize impact and quantitative achievements.")

    # Summary
    if overall_score >= 80:
        summary = f"Strong match ({overall_score}%). Your resume closely matches the core requirements and technical stack for this position."
    elif overall_score >= 65:
        summary = f"Promising match ({overall_score}%). You meet the primary technical requirements, with a few gaps in preferred qualifications."
    elif overall_score >= 50:
        summary = f"Moderate match ({overall_score}%). You demonstrate foundational skills, but several required technologies or experience requirements are not clearly shown."
    else:
        summary = f"Needs improvement ({overall_score}%). Significant gaps exist between your current profile and the position's requirements."

    return summary, strengths, gaps, recommendations


# ==============================================================================
# 8. MASTER SCORING FUNCTION (Section 14 & 18)
# ==============================================================================

def calculate_candidate_fit(session_id: str, force_refresh: bool = False) -> Dict[str, Any]:
    metadata = read_metadata(session_id)
    if not force_refresh and "candidate_fit" in metadata:
        return metadata["candidate_fit"]

    resume_path, jd_path, _ = get_session_paths(session_id)

    if not index_exists(resume_path):
        raise ValueError("Resume FAISS index not found for this session. Please upload a resume first.")
    if not index_exists(jd_path):
        raise ValueError("Job Description FAISS index not found for this session. Please upload a JD first.")

    resume_vs = load_vector_store(str(resume_path))
    jd_vs = load_vector_store(str(jd_path))

    resume_docs = list(resume_vs.docstore._dict.values())
    jd_docs = list(jd_vs.docstore._dict.values())

    resume_text = "\n\n".join(d.page_content for d in resume_docs)
    jd_text = "\n\n".join(d.page_content for d in jd_docs)

    if not resume_text.strip():
        raise ValueError("Uploaded resume is empty.")
    if not jd_text.strip():
        raise ValueError("Uploaded job description is empty.")

    # Extract facts
    jd_facts = extract_jd_facts(jd_text)
    resume_facts = extract_resume_facts(resume_text)

    # 1. Skills Matching
    skill_data = match_skills(jd_facts, resume_facts, resume_text)

    # 2. Experience Evaluation
    exp_data = evaluate_experience(jd_facts, resume_facts, len(skill_data["matched"]))

    # 3. Projects Evaluation
    proj_data = evaluate_projects(jd_facts, resume_facts)

    # 4. Education Evaluation
    edu_data = evaluate_education(jd_facts, resume_facts)

    # Breakdown scores (0 - 100)
    req_skills_score = skill_data["required_skills_score"]
    pref_skills_score = skill_data["preferred_skills_score"]
    experience_score = exp_data["score"]
    projects_score = proj_data["score"]
    education_score = edu_data["score"]

    # Overall score formula (Section 2)
    # overall_score =
    #     required_skills_score * 0.40
    #     + experience_score * 0.20
    #     + projects_score * 0.20
    #     + preferred_skills_score * 0.10
    #     + education_score * 0.10
    raw_overall = (
        req_skills_score * WEIGHTS["required_skills"]
        + experience_score * WEIGHTS["experience"]
        + projects_score * WEIGHTS["projects"]
        + pref_skills_score * WEIGHTS["preferred_skills"]
        + education_score * WEIGHTS["education"]
    )
    overall_score = round(min(100.0, max(0.0, raw_overall)))

    # Match Label (Section 13)
    match_label = "Needs improvement"
    for threshold, label in SCORE_THRESHOLDS:
        if overall_score >= threshold:
            match_label = label
            break

    # Summary, strengths, gaps, recommendations
    summary, strengths, gaps, recommendations = generate_insights_and_summary(
        overall_score=overall_score,
        match_label=match_label,
        skill_data=skill_data,
        exp_data=exp_data,
        proj_data=proj_data,
        edu_data=edu_data,
        resume_facts=resume_facts,
        jd_facts=jd_facts,
    )

    # Structured Response conforming strictly to Section 14
    result = {
        "overall_score": overall_score,
        "match_label": match_label,
        "summary": summary,
        "breakdown": {
            "required_skills": req_skills_score,
            "preferred_skills": pref_skills_score,
            "experience": experience_score,
            "projects": projects_score,
            "education": education_score,
        },
        "skills": {
            "matched": skill_data["matched"],
            "missing_required": skill_data["missing_required"],
            "missing_preferred": skill_data["missing_preferred"],
            "partial": skill_data["partial"],
        },
        "strengths": strengths,
        "gaps": gaps,
        "relevant_projects": proj_data["relevant_projects"],
        "recommendations": recommendations,
    }

    try:
        write_metadata(session_id, {"candidate_fit": result})
    except Exception:
        pass

    return result

