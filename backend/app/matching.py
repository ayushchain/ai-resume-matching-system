"""Matching engine.

Score = 0.45 * Semantic + 0.35 * Skill Coverage + 0.20 * Experience

Semantic similarity:
  - Preferred: sentence-transformers (all-MiniLM-L6-v2) embeddings + cosine.
  - Fallback : TF-IDF (sklearn) vectors + cosine — activates automatically
               if the transformer model cannot be loaded (offline etc.).
               The API reports which method was used; the demo never crashes.
"""
import logging

logger = logging.getLogger(__name__)

_model = None
_method = None  # "sentence-transformers" or "tfidf"
_load_tried = False


def _get_model():
    global _model, _method, _load_tried
    if _load_tried:
        return _model
    _load_tried = True
    try:
        from sentence_transformers import SentenceTransformer
        _model = SentenceTransformer("all-MiniLM-L6-v2")
        _method = "sentence-transformers (all-MiniLM-L6-v2)"
        logger.info("Semantic method: %s", _method)
    except Exception as exc:  # offline, download blocked, not installed...
        logger.warning("Transformer unavailable (%s) -> TF-IDF fallback", exc)
        _model = None
        _method = "tfidf (fallback)"
    return _model


def semantic_scores(jd_text: str, resume_texts: list[str]) -> tuple[list[float], str]:
    """Return (scores 0-100 per resume, method name used)."""
    model = _get_model()
    if model is not None:
        import numpy as np
        embs = model.encode([jd_text] + resume_texts, normalize_embeddings=True)
        jd_emb, res_embs = embs[0], embs[1:]
        sims = (res_embs @ jd_emb)  # cosine, since normalised
        # Raw cosine for this model typically sits ~0.1-0.7 for related text.
        # Rescale gently so scores spread readably: score = clamp(sim*130)
        scores = [float(min(100.0, max(0.0, s * 130))) for s in sims]
        return scores, _method
    # --- TF-IDF fallback ---
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    try:
        vec = TfidfVectorizer(stop_words="english", max_features=5000)
        matrix = vec.fit_transform([jd_text] + resume_texts)
        sims = cosine_similarity(matrix[0:1], matrix[1:]).flatten()
    except ValueError:
        sims = [0.0] * len(resume_texts)
    scores = [float(min(100.0, max(0.0, s * 140))) for s in sims]
    return scores, "tfidf (fallback)"


def experience_score(candidate_years: float, required_years: float, has_exp_section: bool) -> float:
    if required_years and required_years > 0:
        return 100.0 if candidate_years >= required_years else round(candidate_years / required_years * 100, 1)
    # JD states no years: neutral band based on having experience at all
    return 90.0 if has_exp_section and candidate_years > 0 else 60.0


def score_candidate(jd: dict, cand: dict, semantic: float) -> dict:
    jd_skills = jd["skills"]
    matched = sorted(set(jd_skills) & set(cand["skills"]))
    missing = sorted(set(jd_skills) - set(cand["skills"]))
    skill_cov = (len(matched) / len(jd_skills) * 100) if jd_skills else 0.0
    exp_s = experience_score(cand["experience_years"], jd["required_years"],
                             cand["experience_years"] > 0)
    overall = round(0.45 * semantic + 0.35 * skill_cov + 0.20 * exp_s, 1)

    reasons = [
        f"Semantic similarity is {semantic:.0f}/100 — the resume's overall meaning and wording "
        f"{'closely match' if semantic >= 60 else 'partly match' if semantic >= 35 else 'only weakly match'} the job description.",
        f"Matched {len(matched)} of {len(jd_skills)} required skills"
        + (f" ({', '.join(matched[:6])}{'...' if len(matched) > 6 else ''})." if matched else "."),
    ]
    if missing:
        reasons.append(f"Missing skills: {', '.join(missing[:8])}{'...' if len(missing) > 8 else ''} — these lower the skill coverage score.")
    req = jd["required_years"]
    if req:
        reasons.append(
            f"Experience: candidate has {cand['experience_years']} years vs {req} years required — "
            f"{'meets the requirement.' if cand['experience_years'] >= req else 'below the requirement, so the experience score is reduced proportionally.'}")
    else:
        reasons.append(f"Experience: candidate has {cand['experience_years']} years; the JD did not state a minimum.")

    return {
        "name": cand["name"],
        "file_name": cand["file_name"],
        "email": cand["email"],
        "phone": cand["phone"],
        "education": cand["education"],
        "experience_years": cand["experience_years"],
        "candidate_skills": cand["skills"],
        "matched_skills": matched,
        "missing_skills": missing,
        "scores": {
            "overall": overall,
            "semantic": round(semantic, 1),
            "skill_coverage": round(skill_cov, 1),
            "experience": round(exp_s, 1),
        },
        "experience_comparison": {
            "candidate_years": cand["experience_years"],
            "required_years": req,
            "meets_requirement": bool(req and cand["experience_years"] >= req),
        },
        "reasons": reasons,
    }
