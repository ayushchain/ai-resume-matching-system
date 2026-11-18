"""Unit tests for the scoring formula (app/matching.py).

The formula must stay: Overall = 0.45*Semantic + 0.35*Skill + 0.20*Experience.
The two worked examples are the documented ones from TEST_RESULTS.md.
"""
from app.matching import experience_score, score_candidate

SKILLS_20 = ["Python", "Java", "SQL", "Docker", "Kubernetes", "AWS", "Git",
             "React", "FastAPI", "Django", "Flask", "MongoDB", "PostgreSQL",
             "Redis", "Kafka", "Linux", "Testing", "Pytest", "Agile",
             "System Design"]


def _jd():
    return {"skills": SKILLS_20, "required_years": 3.0, "raw_text": ""}


def _cand(skill_count=16, years=5.0):
    return {"name": "Test Candidate", "file_name": "test.pdf", "email": None,
            "phone": None, "education": [], "experience_years": years,
            "skills": SKILLS_20[:skill_count]}


def test_worked_example_sentence_transformers():
    # TEST_RESULTS section 7, top row: semantic 93.0, skill coverage 80
    # (16 of 20), experience 100 -> overall 89.8.
    result = score_candidate(_jd(), _cand(), 93.0)
    assert result["scores"]["skill_coverage"] == 80.0
    assert result["scores"]["experience"] == 100
    assert result["scores"]["overall"] == 89.8


def test_worked_example_tfidf():
    # README worked example: semantic 59.3, skill 80, experience 100 -> 74.7.
    result = score_candidate(_jd(), _cand(), 59.3)
    assert result["scores"]["overall"] == 74.7


def test_experience_score_proportional_below_requirement():
    assert experience_score(2.0, 3.0, True) == 66.7
    assert experience_score(3.0, 3.0, True) == 100.0
    assert experience_score(6.0, 3.0, True) == 100.0


def test_matched_and_missing_skills():
    result = score_candidate(_jd(), _cand(skill_count=16), 50.0)
    assert len(result["matched_skills"]) == 16
    assert len(result["missing_skills"]) == 4
    assert result["experience_comparison"]["meets_requirement"] is True
