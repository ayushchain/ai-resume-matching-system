"""Resume / JD parsing: file -> text, then text -> structured fields."""
import io
import re

import fitz  # PyMuPDF
from docx import Document

from .skills import extract_skills

EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
PHONE_RE = re.compile(r"(\+?\d[\d\s\-()]{8,}\d)")


def extract_text(filename: str, data: bytes) -> str:
    """Extract plain text from PDF, DOCX or TXT bytes."""
    name = filename.lower()
    if name.endswith(".pdf"):
        doc = fitz.open(stream=data, filetype="pdf")
        return "\n".join(page.get_text() for page in doc)
    if name.endswith(".docx"):
        doc = Document(io.BytesIO(data))
        return "\n".join(p.text for p in doc.paragraphs)
    if name.endswith(".txt"):
        return data.decode("utf-8", errors="ignore")
    raise ValueError(f"Unsupported file type: {filename} (use PDF, DOCX or TXT)")


def _guess_name(text: str) -> str:
    """Heuristic: first non-empty line that looks like a person's name."""
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        if "@" in line or "http" in line.lower() or len(line) > 45:
            continue
        words = line.split()
        if 2 <= len(words) <= 4 and all(w[0].isalpha() for w in words):
            return line.title()
        return line[:45]
    return "Unknown Candidate"


def extract_experience_years(text: str) -> float:
    """Estimate total experience years.

    Strategy (simple + explainable):
    1. Explicit 'X years of experience' / 'X+ years' -> take the largest.
    2. Else date ranges like 2021 - 2024 / 2020-Present -> sum the spans.
    3. Else 0.
    """
    low = text.lower()
    explicit = [float(x) for x in re.findall(r"(\d+(?:\.\d+)?)\s*\+?\s*years?\s+(?:of\s+)?experience", low)]
    explicit += [float(x) for x in re.findall(r"experience\s*[:\-]?\s*(\d+(?:\.\d+)?)\s*\+?\s*years?", low)]
    if explicit:
        return max(explicit)

    total = 0.0
    current_year = 2026
    for start, end in re.findall(r"(20\d{2})\s*[-–to]+\s*(20\d{2}|present|current|now)", low):
        s = int(start)
        e = current_year if end in ("present", "current", "now") else int(end)
        if e >= s:
            total += (e - s)
    return round(total, 1)


def extract_required_years(jd_text: str) -> float:
    """Minimum years the JD asks for, e.g. '3+ years' -> 3. 0 if unstated."""
    low = jd_text.lower()
    hits = [float(x) for x in re.findall(r"(\d+(?:\.\d+)?)\s*\+?\s*years?", low)]
    return min(hits) if hits else 0.0


def parse_candidate(filename: str, text: str) -> dict:
    email = EMAIL_RE.search(text)
    phone = PHONE_RE.search(text)
    edu_lines = [ln.strip() for ln in text.splitlines()
                 if any(k in ln.lower() for k in ("b.tech", "btech", "b.e.", "m.tech", "mtech",
                                                  "bachelor", "master", "mba", "bca", "mca", "phd"))]
    return {
        "file_name": filename,
        "name": _guess_name(text),
        "email": email.group(0) if email else None,
        "phone": phone.group(0).strip() if phone else None,
        "skills": extract_skills(text),
        "experience_years": extract_experience_years(text),
        "education": edu_lines[:2],
        "raw_text": text,
    }


def parse_jd(text: str) -> dict:
    quals = [ln.strip() for ln in text.splitlines()
             if any(k in ln.lower() for k in ("bachelor", "master", "degree", "qualification", "b.tech", "m.tech"))]
    return {
        "skills": extract_skills(text),
        "required_years": extract_required_years(text),
        "qualifications": quals[:3],
        "raw_text": text,
    }
