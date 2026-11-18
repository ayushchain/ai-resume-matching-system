"""Persistence for ranking runs — stdlib sqlite3 only, no new dependencies.

Every POST /api/rank saves its run and per-candidate results to
backend/data/runs.db, so past rankings can be reviewed through
GET /api/history. SQLite keeps the prototype dependency-free; PostgreSQL
is the documented production upgrade path (see docs/APPROACH.md).
"""
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "runs.db"

_SCHEMA = """
CREATE TABLE IF NOT EXISTS runs (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at      TEXT NOT NULL,
    jd_skills       TEXT NOT NULL,          -- JSON list of JD skill names
    required_years  REAL NOT NULL DEFAULT 0,
    semantic_method TEXT NOT NULL,
    candidate_count INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS results (
    run_id          INTEGER NOT NULL REFERENCES runs(id),
    rank            INTEGER NOT NULL,
    name            TEXT NOT NULL,
    overall         REAL NOT NULL,
    semantic        REAL NOT NULL,
    skill_coverage  REAL NOT NULL,
    experience_score REAL NOT NULL,
    years           REAL NOT NULL
);
"""


def _connect() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.executescript(_SCHEMA)
    return conn


def save_run(jd: dict, semantic_method: str, results: list[dict]) -> int:
    """Store one ranking run and its results; return the new run id."""
    created_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    with _connect() as conn:
        cur = conn.execute(
            "INSERT INTO runs (created_at, jd_skills, required_years, semantic_method, candidate_count)"
            " VALUES (?, ?, ?, ?, ?)",
            (created_at, json.dumps(jd["skills"]), jd["required_years"],
             semantic_method, len(results)),
        )
        run_id = cur.lastrowid
        conn.executemany(
            "INSERT INTO results (run_id, rank, name, overall, semantic, skill_coverage,"
            " experience_score, years) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            [(run_id, r["rank"], r["name"], r["scores"]["overall"], r["scores"]["semantic"],
              r["scores"]["skill_coverage"], r["scores"]["experience"], r["experience_years"])
             for r in results],
        )
    return run_id


def list_runs(limit: int = 20) -> list[dict]:
    """Most recent runs, each with its top candidate's name and score."""
    with _connect() as conn:
        rows = conn.execute(
            "SELECT r.id, r.created_at, r.jd_skills, r.required_years, r.semantic_method,"
            " r.candidate_count, t.name AS top_name, t.overall AS top_score"
            " FROM runs r LEFT JOIN results t ON t.run_id = r.id AND t.rank = 1"
            " ORDER BY r.id DESC LIMIT ?",
            (limit,),
        ).fetchall()
    return [{
        "id": row["id"],
        "created_at": row["created_at"],
        "jd_skill_count": len(json.loads(row["jd_skills"])),
        "required_years": row["required_years"],
        "semantic_method": row["semantic_method"],
        "candidate_count": row["candidate_count"],
        "top_candidate": row["top_name"],
        "top_score": row["top_score"],
    } for row in rows]


def get_run(run_id: int) -> dict | None:
    """One stored run with its full ranked results, or None if not found."""
    with _connect() as conn:
        run = conn.execute("SELECT * FROM runs WHERE id = ?", (run_id,)).fetchone()
        if run is None:
            return None
        rows = conn.execute(
            "SELECT rank, name, overall, semantic, skill_coverage, experience_score, years"
            " FROM results WHERE run_id = ? ORDER BY rank",
            (run_id,),
        ).fetchall()
    return {
        "id": run["id"],
        "created_at": run["created_at"],
        "jd_skills": json.loads(run["jd_skills"]),
        "required_years": run["required_years"],
        "semantic_method": run["semantic_method"],
        "candidate_count": run["candidate_count"],
        "results": [dict(row) for row in rows],
    }
