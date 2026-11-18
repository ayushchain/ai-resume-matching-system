"""Unit tests for skill extraction (app/skills.py)."""
from app.skills import extract_skills


def test_known_skills_found():
    found = extract_skills("Backend developer with Python, FastAPI and PostgreSQL experience.")
    assert "Python" in found
    assert "FastAPI" in found
    assert "PostgreSQL" in found


def test_aliases_resolve_to_canonical_names():
    found = extract_skills("Worked with JS, k8s and postgres in production.")
    assert "JavaScript" in found
    assert "Kubernetes" in found
    assert "PostgreSQL" in found


def test_java_does_not_match_inside_javascript():
    found = extract_skills("JavaScript and TypeScript developer")
    assert "JavaScript" in found
    assert "Java" not in found


def test_java_matches_when_standalone():
    found = extract_skills("Java developer using Spring Boot")
    assert "Java" in found
    assert "Spring Boot" in found


def test_empty_text_gives_no_skills():
    assert extract_skills("") == []
    assert extract_skills(None) == []
