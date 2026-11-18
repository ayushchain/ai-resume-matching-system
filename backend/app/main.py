"""FastAPI app: JD analysis + batch resume ranking.

Run:  uvicorn app.main:app --reload --port 8000   (from backend/)
"""
import logging

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from . import store
from .matching import score_candidate, semantic_scores
from .parsers import extract_text, parse_candidate, parse_jd

logger = logging.getLogger(__name__)

app = FastAPI(title="Resume Matching & Candidate Ranking System", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.post("/api/jd/analyze")
async def analyze_jd(jd_text: str = Form(default=""), jd_file: UploadFile | None = File(default=None)):
    """Accept JD as pasted text OR an uploaded file; return extracted requirements."""
    text = jd_text or ""
    if jd_file is not None and jd_file.filename:
        text = extract_text(jd_file.filename, await jd_file.read())
    if not text.strip():
        return {"error": "Provide a job description as text or file."}
    jd = parse_jd(text)
    return {"skills": jd["skills"], "required_years": jd["required_years"],
            "qualifications": jd["qualifications"], "char_count": len(text)}


@app.post("/api/rank")
async def rank(jd_text: str = Form(default=""), jd_file: UploadFile | None = File(default=None),
               resumes: list[UploadFile] = File(...)):
    """Batch-rank resumes against a JD. Supports 10+ files in one request."""
    text = jd_text or ""
    if jd_file is not None and jd_file.filename:
        text = extract_text(jd_file.filename, await jd_file.read())
    if not text.strip():
        return {"error": "Provide a job description as text or file."}

    jd = parse_jd(text)
    candidates, errors = [], []
    for f in resumes:
        try:
            raw = extract_text(f.filename, await f.read())
            if raw.strip():
                candidates.append(parse_candidate(f.filename, raw))
            else:
                errors.append({"file": f.filename, "error": "No text could be extracted"})
        except Exception as exc:
            errors.append({"file": f.filename, "error": str(exc)})

    if not candidates:
        return {"error": "No readable resumes were uploaded.", "file_errors": errors}

    sem_scores, method = semantic_scores(jd["raw_text"], [c["raw_text"] for c in candidates])
    results = [score_candidate(jd, c, s) for c, s in zip(candidates, sem_scores)]
    results.sort(key=lambda r: r["scores"]["overall"], reverse=True)
    for i, r in enumerate(results, start=1):
        r["rank"] = i

    # Persist the run for /api/history. Storage is best-effort only: a
    # failure here must never break the ranking response.
    run_id = None
    try:
        run_id = store.save_run(jd, method, results)
    except Exception as exc:
        logger.warning("Could not save ranking run to history: %s", exc)

    return {
        "run_id": run_id,
        "semantic_method": method,
        "jd_summary": {"skills": jd["skills"], "required_years": jd["required_years"],
                       "qualifications": jd["qualifications"]},
        "total_candidates": len(results),
        "results": results,
        "file_errors": errors,
    }


@app.get("/api/history")
def history():
    """Most recent saved ranking runs, newest first."""
    return {"runs": store.list_runs()}


@app.get("/api/history/{run_id}")
def history_run(run_id: int):
    """Full stored results for one past run."""
    run = store.get_run(run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="Run not found")
    return run
