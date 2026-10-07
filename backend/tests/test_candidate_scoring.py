import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from rag.candidate_scorer import (
    WEIGHTS,
    SEMANTIC_MATCH_THRESHOLD,
    SEMANTIC_PARTIAL_LOW,
    PARTIAL_MATCH_CREDIT,
    normalize_skill_name,
    are_mutually_exclusive,
    is_skill_explicitly_present,
    match_skills,
    evaluate_experience,
    evaluate_projects,
    evaluate_education,
    JDFacts,
    ResumeFacts,
    ResumeRole,
    ResumeProject,
)


class TestCandidateScoring(unittest.TestCase):
    def test_weights_sum_to_one(self):
        total_weight = sum(WEIGHTS.values())
        self.assertAlmostEqual(total_weight, 1.0, places=6)
        self.assertEqual(WEIGHTS["required_skills"], 0.40)
        self.assertEqual(WEIGHTS["experience"], 0.20)
        self.assertEqual(WEIGHTS["projects"], 0.20)
        self.assertEqual(WEIGHTS["preferred_skills"], 0.10)
        self.assertEqual(WEIGHTS["education"], 0.10)

    def test_mutually_exclusive_skills(self):
        self.assertTrue(are_mutually_exclusive("Java", "JavaScript"))
        self.assertTrue(are_mutually_exclusive("Java", "TypeScript"))
        self.assertTrue(are_mutually_exclusive("C", "C++"))
        self.assertTrue(are_mutually_exclusive("C++", "C#"))
        self.assertTrue(are_mutually_exclusive("JavaScript", "TypeScript"))
        self.assertFalse(are_mutually_exclusive("Python", "Python"))
        self.assertFalse(are_mutually_exclusive("React", "Vue"))

    def test_normalization(self):
        self.assertEqual(normalize_skill_name("react.js"), "React")
        self.assertEqual(normalize_skill_name("React"), "React")
        self.assertEqual(normalize_skill_name("nodejs"), "Node.js")
        self.assertEqual(normalize_skill_name("RESTful API development"), "REST APIs")
        self.assertEqual(normalize_skill_name("postgres"), "PostgreSQL")

    def test_required_skill_priority_and_no_duplicates(self):
        jd = JDFacts(
            required_skills=["Redis", "Python", "React"],
            preferred_skills=["Redis", "Docker"],
        )
        resume = ResumeFacts(
            skills=["Python", "React"],
        )
        resume_text = "I work with Python and React."

        result = match_skills(jd, resume, resume_text)

        # Redis must be in missing_required, and NOT in missing_preferred
        self.assertIn("Redis", result["missing_required"])
        self.assertNotIn("Redis", result["missing_preferred"])
        self.assertNotIn("Redis", result["matched"])

        # No category overlap
        all_skills = (
            result["matched"]
            + result["missing_required"]
            + result["missing_preferred"]
            + result["partial"]
        )
        self.assertEqual(len(all_skills), len(set(s.casefold() for s in all_skills)))

    def test_preferred_skills_do_not_affect_required_skills(self):
        jd = JDFacts(
            required_skills=["React", "Node.js"],
            preferred_skills=["Redis"],
        )
        resume = ResumeFacts(
            skills=["React", "Redis"],
        )
        resume_text = "Experienced in React and Redis."

        result = match_skills(jd, resume, resume_text)

        # React is 1 of 2 required skills (50%)
        self.assertEqual(result["required_skills_score"], 50)
        # Redis is 1 of 1 preferred skills (100%)
        self.assertEqual(result["preferred_skills_score"], 100)

    def test_no_preferred_skills_yields_100(self):
        jd = JDFacts(
            required_skills=["Python"],
            preferred_skills=[],
        )
        resume = ResumeFacts(skills=["Python"])
        result = match_skills(jd, resume, "Python developer")
        self.assertEqual(result["preferred_skills_score"], 100)
        self.assertEqual(result["required_skills_score"], 100)

    def test_no_required_skills_yields_100(self):
        jd = JDFacts(
            required_skills=[],
            preferred_skills=["Docker"],
        )
        resume = ResumeFacts(skills=[])
        result = match_skills(jd, resume, "")
        self.assertEqual(result["required_skills_score"], 100)
        self.assertEqual(result["preferred_skills_score"], 0)

    def test_education_not_mentioned_yields_100(self):
        jd = JDFacts(
            education_degree=None,
            education_fields=[],
        )
        resume = ResumeFacts()
        result = evaluate_education(jd, resume)
        self.assertEqual(result["score"], 100)

    def test_education_matching(self):
        jd = JDFacts(
            education_degree="Bachelor",
            education_fields=["Computer Science"],
        )
        resume = ResumeFacts(
            degree="B.Tech",
            field="Computer Science & Engineering",
        )
        result = evaluate_education(jd, resume)
        self.assertEqual(result["score"], 100)

    def test_experience_evaluation_entry_level(self):
        jd = JDFacts(min_experience_years=0.0)
        resume = ResumeFacts(
            experience_years=0.5,
            has_internship=True,
            roles=[ResumeRole(title="Software Engineer Intern")],
        )
        result = evaluate_experience(jd, resume, matched_skills_count=4)
        self.assertGreaterEqual(result["score"], 90)

    def test_experience_evaluation_senior_gap(self):
        jd = JDFacts(min_experience_years=5.0)
        resume = ResumeFacts(
            experience_years=0.5,
            has_internship=True,
        )
        result = evaluate_experience(jd, resume, matched_skills_count=2)
        # Should reduce experience score
        self.assertLessEqual(result["score"], 60)

    def test_projects_evaluation(self):
        jd = JDFacts(required_skills=["React", "Node.js", "MongoDB"])
        resume = ResumeFacts(
            projects=[
                ResumeProject(
                    name="Collab-Docs",
                    technologies=["React", "Node.js", "MongoDB"],
                    description="Real-time document editor",
                ),
                ResumeProject(
                    name="Weather App",
                    technologies=["HTML", "CSS"],
                    description="Simple weather app",
                ),
            ]
        )
        result = evaluate_projects(jd, resume)
        self.assertGreaterEqual(result["score"], 0)
        self.assertLessEqual(result["score"], 100)
        self.assertLessEqual(len(result["relevant_projects"]), 3)
        self.assertEqual(result["relevant_projects"][0]["name"], "Collab-Docs")
        self.assertGreaterEqual(result["relevant_projects"][0]["relevance"], 80)


if __name__ == "__main__":
    unittest.main()
