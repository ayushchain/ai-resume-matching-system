# Test Results — actual runs, 2026-11-15

Environment: Python 3.12 venv, Node 24 / Vite 5. Backend started with
`uvicorn app.main:app --port 8000`.

## 1. Backend health
`GET /api/health` → `{"status":"ok"}` ✅

## 2. JD analysis endpoint
Input (pasted text): "We need a Python developer with 2+ years experience,
FastAPI, SQL and Docker skills. Bachelor degree required."
Output: skills = [Docker, FastAPI, Python, SQL], required_years = 2.0 ✅

## 3. End-to-end ranking — sample JD + all 12 sample resumes (one batch)
Request: `POST /api/rank` with `sample_data/sample_jd.txt` as the JD file and
all 12 PDFs from `sample_data/resumes/`. All 12 parsed, **0 file errors**.

**Semantic method used: `tfidf (fallback)`** — sentence-transformers could
not be installed in the test environment (pip download failed with a network
connectivity error), so the automatic fallback activated exactly as designed
and the API reported it in `semantic_method`. On a machine with internet,
the same code loads `all-MiniLM-L6-v2` first.

JD detected: 20 skills, required experience 3.0 years.

| Rank | Candidate | Overall | Semantic | Skill cov. | Exp score | Years | Matched |
|---|---|---|---|---|---|---|---|
| 1 | Aarav Sharma | 74.7 | 59.3 | 80.0 | 100 | 5 | 16/20 |
| 2 | Vikram Singh | 62.9 | 48.6 | 60.0 | 100 | 6 | 12/20 |
| 3 | Priya Nair | 57.1 | 39.7 | 55.0 | 100 | 4 | 11/20 |
| 4 | Rohan Verma | 49.7 | 34.9 | 40.0 | 100 | 3 | 8/20 |
| 5 | Karan Malhotra | 46.7 | 32.0 | 35.0 | 100 | 5 | 7/20 |
| 6 | Kavya Reddy | 45.7 | 26.1 | 40.0 | 100 | 4 | 8/20 |
| 7 | Sneha Kulkarni | 42.0 | 25.6 | 30.0 | 100 | 3 | 6/20 |
| 8 | Ananya Iyer | 36.4 | 21.0 | 20.0 | 100 | 3 | 4/20 |
| 9 | Arjun Mehta | 35.4 | 25.7 | 30.0 | 66.7 | 2 | 6/20 |
| 10 | Rahul Patil | 24.9 | 14.1 | 15.0 | 66.7 | 2 | 3/20 |
| 11 | Divya Menon | 16.5 | 10.3 | 15.0 | 33.3 | 1 | 3/20 |
| 12 | Meera Joshi | 6.6 | 10.8 | 5.0 | 0 | 0 | 1/20 |

Sanity check ✅ — the ranking matches human judgement: the Python/FastAPI
specialist is #1, the DevOps engineer with partial overlap is mid-table,
the data scientist and the fresher with no backend skills are at the bottom.

## 4. DOCX resume test
A DOCX resume generated with python-docx (Python, FastAPI, SQL, Docker, Git;
3 years) was uploaded against the same JD → parsed correctly:
name extracted, overall 43.8, matched skills [Docker, FastAPI, Git, Python, SQL] ✅

## 5. Frontend build
`npm install` ✅ · `npm run build` ✅ (Vite, 31 modules, built in 2.35s,
dist JS 147.66 kB / gzip 47.66 kB)

## Known note
Vikram Singh's resume intentionally mentions "Celery", which is not in the
skill taxonomy — it is correctly ignored, illustrating the taxonomy
limitation documented in the README.
