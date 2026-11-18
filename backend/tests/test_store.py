"""Unit tests for run persistence (app/store.py).

The store's DB_PATH is pointed at a throwaway temp file for the whole
module, so tests never touch the real backend/data/runs.db.
"""
import tempfile
from pathlib import Path

from app import store

store.DB_PATH = Path(tempfile.mkdtemp(prefix="rms-test-")) / "runs.db"

JD = {"skills": ["Python", "FastAPI"], "required_years": 3.0}


def _results():
    rows = [("Top Person", 89.8, 93.0, 80.0, 100.0, 5.0),
            ("Second Person", 70.0, 80.0, 50.0, 100.0, 4.0)]
    return [{"rank": i, "name": name, "experience_years": years,
             "scores": {"overall": overall, "semantic": sem,
                        "skill_coverage": cov, "experience": exp}}
            for i, (name, overall, sem, cov, exp, years) in enumerate(rows, start=1)]


def test_save_run_and_history_list():
    before = len(store.list_runs())
    run_id = store.save_run(JD, "sentence-transformers (all-MiniLM-L6-v2)", _results())
    assert isinstance(run_id, int) and run_id >= 1
    runs = store.list_runs()
    assert len(runs) == before + 1
    latest = runs[0]  # newest first
    assert latest["id"] == run_id
    assert latest["candidate_count"] == 2
    assert latest["jd_skill_count"] == 2
    assert latest["required_years"] == 3.0
    assert latest["top_candidate"] == "Top Person"
    assert latest["top_score"] == 89.8


def test_get_run_returns_full_ranked_results():
    run_id = store.save_run(JD, "tfidf (fallback)", _results())
    run = store.get_run(run_id)
    assert run["semantic_method"] == "tfidf (fallback)"
    assert run["jd_skills"] == ["Python", "FastAPI"]
    assert [r["name"] for r in run["results"]] == ["Top Person", "Second Person"]
    assert run["results"][0]["overall"] == 89.8
    assert run["results"][1]["rank"] == 2
    assert run["results"][1]["years"] == 4.0


def test_get_run_unknown_id_returns_none():
    assert store.get_run(999999) is None
