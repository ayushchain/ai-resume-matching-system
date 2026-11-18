"""Resume / JD parsing: file -> text, then text -> structured fields."""
import io
import re
from datetime import date

import fitz  # PyMuPDF
from docx import Document

from .skills import extract_skills

EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
PHONE_RE = re.compile(r"(\+?\d[\d\s\-()]{8,}\d)")

_MONTHS = {
    "jan": 1, "january": 1, "feb": 2, "february": 2, "mar": 3, "march": 3,
    "apr": 4, "april": 4, "may": 5, "jun": 6, "june": 6, "jul": 7, "july": 7,
    "aug": 8, "august": 8, "sep": 9, "sept": 9, "september": 9, "oct": 10,
    "october": 10, "nov": 11, "november": 11, "dec": 12, "december": 12,
}
_MONTH_RE = (r"(january|february|march|april|june|july|august|september|"
             r"october|november|december|"
             r"jan|feb|mar|apr|may|jun|jul|aug|sept|sep|oct|nov|dec)")
# One date range: [Month] YYYY <sep> ([Month] YYYY | Present), sep = -, –, —, "to"
_RANGE_RE = re.compile(
    rf"(?:{_MONTH_RE}\s+)?(20\d{{2}})\s*(?:[-–—]|to)\s*"
    rf"(?:(?:{_MONTH_RE}\s+)?(20\d{{2}})|(present|current|now))")


def _month_index(year: int, month: int) -> int:
    """Absolute month number, so date spans can be subtracted and merged."""
    return year * 12 + (month - 1)


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
    2. Else date ranges -> sum the spans. Ranges may be year-only
       ('2019 - 2022') or month-year ('Jan 2020 - Mar 2023',
       'Jun 2021 to Present'); 'Present' counts up to today.
       Overlapping ranges are merged, so shared months count once.
    3. Else 0.
    """
    low = text.lower()
    explicit = [float(x) for x in re.findall(r"(\d+(?:\.\d+)?)\s*\+?\s*years?\s+(?:of\s+)?experience", low)]
    explicit += [float(x) for x in re.findall(r"experience\s*[:\-]?\s*(\d+(?:\.\d+)?)\s*\+?\s*years?", low)]
    if explicit:
        return max(explicit)

    # Work in absolute month numbers. Precision follows the input: a
    # year-only date means January of that year, so '2019 - 2022' is
    # exactly 3.0 years, as before.
    today = date.today()
    spans = []
    for m_start, y_start, m_end, y_end, present in _RANGE_RE.findall(low):
        start = _month_index(int(y_start), _MONTHS[m_start] if m_start else 1)
        if present:
            end = _month_index(today.year, today.month if m_start else 1)
        else:
            end = _month_index(int(y_end), _MONTHS[m_end] if m_end else 1)
        if end > start:
            spans.append((start, end))
    if not spans:
        return 0.0
    spans.sort()
    total_months, cur_s, cur_e = 0, spans[0][0], spans[0][1]
    for s, e in spans[1:]:
        if s <= cur_e:  # overlapping or touching: extend the current span
            cur_e = max(cur_e, e)
        else:
            total_months += cur_e - cur_s
            cur_s, cur_e = s, e
    total_months += cur_e - cur_s
    return round(total_months / 12, 1)


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
