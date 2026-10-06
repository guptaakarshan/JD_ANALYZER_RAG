import re


KNOWN_SKILLS = (
    "Python", "Java", "JavaScript", "TypeScript", "React", "Node.js", "FastAPI",
    "Django", "Flask", "SQL", "PostgreSQL", "MySQL", "MongoDB", "Redis",
    "AWS", "Azure", "GCP", "Docker", "Kubernetes", "Git", "REST API", "GraphQL",
    "LangChain", "FAISS", "OpenAI", "TensorFlow", "PyTorch", "Pandas", "NumPy",
    "HTML", "CSS", "Tailwind", "Next.js", "Vue", "Angular", "Spring", "C++",
    "C#", "Excel", "Tableau", "Power BI", "Machine Learning", "Deep Learning",
)

CRITICAL_MARKERS = re.compile(
    r"\b(required|requirement|must|required to|essential|mandatory|minimum|need to)\b",
    re.IGNORECASE,
)
PREFERRED_MARKERS = re.compile(r"\b(preferred|nice to have|bonus|plus|ideally)\b", re.IGNORECASE)
EXPERIENCE_MARKERS = re.compile(r"\b(experience|employment|work history|professional background)\b", re.IGNORECASE)
YEAR_PATTERN = re.compile(r"(\d+)\+?\s+years?", re.IGNORECASE)


def extract_skills(text):
    normalized_text = text.casefold()
    return [
        skill for skill in KNOWN_SKILLS
        if re.search(rf"(?<![a-z0-9]){re.escape(skill.casefold())}(?![a-z0-9])", normalized_text)
    ]


def compare_skills(resume_skills, jd_skills):
    resume_lookup = {skill.casefold(): skill for skill in resume_skills}
    matched = [skill for skill in jd_skills if skill.casefold() in resume_lookup]
    missing = [skill for skill in jd_skills if skill.casefold() not in resume_lookup]
    return {"matched": matched, "missing": missing}


def analyze_candidate_fit(resume_text, jd_text):
    resume_skills = extract_skills(resume_text)
    requirements = extract_requirements(jd_text)
    resume_lookup = {skill.casefold() for skill in resume_skills}

    matched = [item["skill"] for item in requirements if item["skill"].casefold() in resume_lookup]
    missing = [item["skill"] for item in requirements if item["skill"].casefold() not in resume_lookup]
    weighted_total = sum(item["weight"] for item in requirements)
    weighted_matched = sum(item["weight"] for item in requirements if item["skill"].casefold() in resume_lookup)
    skill_match_percentage = _percentage(len(matched), len(requirements))
    requirement_coverage = _percentage(weighted_matched, weighted_total)
    experience_relevance = _experience_relevance(resume_text, jd_text, matched, requirements)
    role_fit_score = round(
        (skill_match_percentage * 0.35)
        + (requirement_coverage * 0.45)
        + (experience_relevance["score"] * 0.20)
    )

    missing_qualifications = [
        {
            "skill": item["skill"],
            "criticality": item["criticality"],
            "reason": "Required by the role" if item["criticality"] == "high" else "Listed as a preferred qualification",
        }
        for item in requirements
        if item["skill"].casefold() not in resume_lookup
    ]

    return {
        "matched": matched,
        "missing": missing,
        "requirements": requirements,
        "missing_qualifications": missing_qualifications,
        "skill_match_percentage": skill_match_percentage,
        "requirement_coverage": requirement_coverage,
        "experience_relevance": experience_relevance,
        "role_fit_score": role_fit_score,
        "score_breakdown": {
            "Skills": skill_match_percentage,
            "Requirements": requirement_coverage,
            "Experience": experience_relevance["score"],
        },
    }


def extract_requirements(jd_text):
    requirements = []
    normalized_text = jd_text.casefold()
    for skill in KNOWN_SKILLS:
        match = re.search(
            rf"(?<![a-z0-9]){re.escape(skill.casefold())}(?![a-z0-9])",
            normalized_text,
        )
        if not match:
            continue

        context = jd_text[max(0, match.start() - 140):min(len(jd_text), match.end() + 140)]
        if CRITICAL_MARKERS.search(context):
            criticality, weight = "high", 2.0
        elif PREFERRED_MARKERS.search(context):
            criticality, weight = "low", 0.75
        else:
            criticality, weight = "medium", 1.0

        requirements.append({
            "skill": skill,
            "criticality": criticality,
            "weight": weight,
        })

    return requirements


def _experience_relevance(resume_text, jd_text, matched, requirements):
    resume_has_experience = bool(EXPERIENCE_MARKERS.search(resume_text))
    jd_mentions_experience = bool(EXPERIENCE_MARKERS.search(jd_text))
    matched_ratio = _percentage(len(matched), len(requirements))
    resume_years = _years_from_text(resume_text)
    required_years = _years_from_text(jd_text)

    if not resume_has_experience:
        return {"score": 25, "summary": "Your resume does not clearly describe previous work experience."}

    score = 55 + round(matched_ratio * 0.35)
    if jd_mentions_experience and resume_years and required_years:
        score += 10 if resume_years >= required_years else 3
    score = min(score, 100)
    if matched:
        summary = f"Your background shows relevant experience across {len(matched)} role skill{'s' if len(matched) != 1 else ''}."
    else:
        summary = "Your resume shows experience, but the strongest role skills are not clearly connected to it."
    return {"score": score, "summary": summary}


def _years_from_text(text):
    years = [int(value) for value in YEAR_PATTERN.findall(text)]
    return max(years, default=0)


def _percentage(numerator, denominator):
    if not denominator:
        return 0
    return round((numerator / denominator) * 100)
