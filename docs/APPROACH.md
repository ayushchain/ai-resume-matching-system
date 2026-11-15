# Technical Approach — AI-Based Resume Matching & Candidate Ranking System

*Ayush Raj*

## Problem
A recruiter screening many applications manually reads every resume against
the job description. This prototype automates the first screening pass: it
compares a batch of resumes with one JD and produces a ranked shortlist with
an explainable score for every candidate.

## How it works, step by step
1. **JD analysis** — the JD text (pasted or uploaded) is scanned for skills
   from a curated taxonomy, the required years of experience, and
   qualifications such as the degree level.
2. **Resume parsing** — each uploaded PDF/DOCX is converted to text
   (PyMuPDF for PDF, python-docx for DOCX). Name, email, phone, education,
   skills and total years of experience are extracted with regex and simple
   heuristics ("X years of experience" first, then date ranges).
3. **Matching** — every resume is scored against the JD on three components
   (below) and the results are sorted into the ranking dashboard.
4. **Explanation** — for each candidate the API returns the three component
   scores, matched and missing skills, the experience comparison, and
   plain-English reasons generated from those components.

## Matching algorithm
```
Overall = 0.45 × Semantic Similarity + 0.35 × Skill Coverage + 0.20 × Experience Score
```
- **Semantic similarity (45%)** — JD and resume are converted to vectors
  (Sentence Transformer embeddings from `all-MiniLM-L6-v2`; TF-IDF vectors
  as an automatic fallback if the model cannot be loaded) and compared with
  cosine similarity. This matches *meaning*, not only exact keywords, so a
  resume describing "REST API development with a Python framework" still
  scores well against a FastAPI JD.
- **Skill coverage (35%)** — skills found in the resume divided by the total
  skills the JD asks for, × 100. This step also produces the matched and
  missing skill lists. Skill matching uses word boundaries and aliases, so
  "Java" does not match inside "JavaScript", and "JS" counts as JavaScript.
- **Experience score (20%)** — 100 when the candidate meets or exceeds the
  JD's required years, otherwise candidate ÷ required × 100. If the JD
  states no years, a neutral band is used.

Weights were chosen so meaning is the strongest signal, hard skill
requirements stay decisive, and a capable candidate slightly below the
experience bar is not rejected outright. All weights are constants in
`backend/app/matching.py`, so they can be tuned per role family.

## Design choices
- **Stateless API** — parsing and scoring happen in one request; nothing is
  stored, which keeps the prototype simple and avoids holding candidate
  data. PostgreSQL persistence is the documented next step.
- **Per-file error isolation** — one unreadable file in a batch is reported
  in an error list and does not fail the other resumes.
- **Fallback by design** — if the transformer model is unavailable, the
  system switches to TF-IDF and reports the method used in the response
  (`semantic_method`), instead of failing.

## Limitations
- Skill extraction is taxonomy-based; a skill outside the list in
  `backend/app/skills.py` is missed (the list is one editable file).
- Experience parsing is heuristic and can misread unusual resume layouts.
- Scores are a screening aid, not a hiring decision — the breakdown exists
  so a recruiter can judge the reasoning behind every score.
