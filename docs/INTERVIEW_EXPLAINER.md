# Interview Explainer — simple words me poora project

## What does this app do?
A recruiter pastes a Job Description and uploads many resumes together
(10+ at once). The app reads every resume, compares it with the JD, gives
each candidate a score from 0 to 100, and shows a ranked list — best match
on top. Clicking a candidate shows *why* they got that score.

## How is the score calculated?
Three parts, fixed weights — ye formula yaad kar lo:

```
Overall = 45% Semantic Similarity + 35% Skill Coverage + 20% Experience
```

1. **Semantic similarity** — meaning match (details below).
2. **Skill coverage** — JD ki skills me se kitni resume me mili.
   Example: JD me 20 skills, resume me 16 mili → 80/100.
3. **Experience** — JD ko 3 saal chahiye, candidate ke paas 5 saal → 100.
   Agar 2 saal hote → 2/3 × 100 = 66.7.

Example: 0.45×59.3 + 0.35×80 + 0.20×100 = **74.7** (our top sample candidate).

## What are embeddings / semantic similarity?
An **embedding** converts a piece of text into a list of numbers (a vector)
in such a way that texts with similar *meaning* get similar numbers.
"Built REST APIs in Python" and "FastAPI backend development" use different
words but their vectors point in almost the same direction.
**Cosine similarity** measures the angle between two vectors: same
direction = very similar (score near 100), unrelated = near 0.
This is why the system is not just keyword matching — wording alag ho,
meaning same ho, to bhi match milta hai.

## What if the AI model does not load?
The code first tries Sentence Transformers (`all-MiniLM-L6-v2`). If the
model cannot be downloaded (no internet), it automatically falls back to
**TF-IDF** vectors + cosine similarity, and the API honestly reports which
method was used. TF-IDF gives more weight to rare, important words
(like "Kubernetes") and less to common words (like "the", "work").

## Likely interview Q&A

**Q1. Why not just keyword matching?**
Keywords miss meaning. A resume saying "backend APIs with a Python
framework" is relevant to a FastAPI JD even without the word FastAPI.
Semantic similarity catches that; skill coverage keeps the score grounded
in concrete requirements. We combine both.

**Q2. How do you extract skills?**
A curated taxonomy of 80+ skills with aliases (e.g. "JS" → JavaScript).
We search with word boundaries so "Java" does not match inside
"JavaScript". Trade-off: a skill missing from the list is missed too —
that is a documented limitation, and the list is easy to extend.

**Q3. How do you parse PDFs and DOCX?**
PyMuPDF extracts text from PDFs; python-docx reads DOCX paragraphs.
Then regex + heuristics extract email, phone, name (first line) and
experience ("X years of experience", or date ranges like 2021–2024).

**Q4. Why these weights — 45/35/20?**
Meaning (semantic) is the strongest signal of overall fit, skills are the
hard requirements, experience matters but a skilled candidate slightly
below the years bar should not be rejected. The weights are constants in
one place (`matching.py`), so they are easy to tune and explain.

**Q5. How does batch upload work?**
FastAPI accepts a list of files in one multipart request. Each file is
parsed independently — one bad file goes to an error list and does not
break the others. All 12 sample resumes rank in a few seconds.

**Q6. Is the score biased by name or college?**
No. The score uses only text similarity, skills and years of experience.
Name/college are displayed for the recruiter but never enter the formula.

**Q7. How would you scale this to 10,000 resumes?**
Pre-compute resume embeddings once and store them (e.g. in PostgreSQL
with pgvector), embed only the JD at query time, and rank with a vector
search. Parsing can move to a background queue (Celery).

**Q8. TF-IDF vs embeddings — difference?**
TF-IDF counts words (weighted by rarity) — it matches *words*.
Embeddings are learned by a neural model — they match *meaning*,
including synonyms and paraphrases. Embeddings are better; TF-IDF is the
reliable, dependency-light fallback.

**Q9. How did you test it?**
12 synthetic resumes with known skill/experience profiles + one sample
JD, run end-to-end through the API. The ranking came out in the expected
order (specialist on top, fresher at the bottom) — see TEST_RESULTS.md.
The frontend production build also passes.

**Q10. What would you improve next?**
Persist results in PostgreSQL, add spaCy NER for better name/education
extraction, larger skill ontology, and a fairness audit of scores.

## 30-second demo script
"Ye mera Resume Matching System hai. Main JD paste karta hoon, 12 resumes
ek saath upload karta hoon — system har resume ko parse karke JD se
semantically compare karta hai, aur 0–100 score ke saath ranking deta hai.
Kisi candidate par click karne se score ka poora breakdown dikhta hai —
matched skills, missing skills, aur score ke reasons. Isiliye ye sirf
keyword matching nahi, ek explainable AI matching hai."
