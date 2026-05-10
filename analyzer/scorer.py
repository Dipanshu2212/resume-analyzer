import re
from analyzer.vectorizer import get_tfidf_similarity


# ──────────────────────────────────────────────────────────────────────────────
# FUNCTION 1: Score keyword overlap between resume and job description
# ──────────────────────────────────────────────────────────────────────────────
def score_keywords(resume_text: str, job_text: str) -> dict:
    """
    Score how well the resume keywords match the job description.
    Uses TF-IDF cosine similarity as the base metric.

    Max score: 35 points

    Args:
        resume_text: Raw resume text
        job_text   : Job description text

    Returns:
        {"score": int, "max": 35, "details": str}
    """
    similarity = get_tfidf_similarity(resume_text, job_text)

    # Scale similarity (0-1) to points (0-35)
    points = round(similarity * 35)

    return {
        "score"  : points,
        "max"    : 35,
        "details": f"Keyword overlap similarity: {round(similarity * 100, 1)}%"
    }


# ──────────────────────────────────────────────────────────────────────────────
# FUNCTION 2: Score presence of key resume sections
# ──────────────────────────────────────────────────────────────────────────────
def score_sections(sections: dict) -> dict:
    """
    Score resume based on presence of essential sections.
    Uses the sections dict already extracted by ner.py.

    Max score: 25 points

    Scoring:
        - Experience     : 8 points
        - Education      : 7 points
        - Skills         : 5 points
        - Summary        : 3 points
        - Projects       : 2 points

    Args:
        sections: Dict from ner.extract_sections() e.g. {"education": True, ...}

    Returns:
        {"score": int, "max": 25, "details": dict of section scores}
    """
    section_weights = {
        "experience"    : 8,
        "education"     : 7,
        "skills"        : 5,
        "summary"       : 3,
        "projects"      : 2,
    }

    details = {}
    total   = 0

    for section, weight in section_weights.items():
        present         = sections.get(section, False)
        earned          = weight if present else 0
        total          += earned
        details[section] = {"present": present, "points": earned, "max": weight}

    return {
        "score"  : total,
        "max"    : 25,
        "details": details
    }


# ──────────────────────────────────────────────────────────────────────────────
# FUNCTION 3: Score resume format and quality signals
# ──────────────────────────────────────────────────────────────────────────────
def score_format(resume_text: str) -> dict:
    """
    Score resume based on format quality signals that ATS systems check.

    Max score: 20 points

    Checks:
        - Has email address        : 5 points
        - Has phone number         : 5 points
        - Adequate length          : 5 points (300-1000 words is ideal)
        - Uses action verbs        : 5 points

    Args:
        resume_text: Raw resume text

    Returns:
        {"score": int, "max": 20, "details": dict}
    """
    details = {}
    total   = 0

    # ── Email present ─────────────────────────────────────────────────────────
    has_email       = bool(re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', resume_text))
    email_pts       = 5 if has_email else 0
    total          += email_pts
    details["email"] = {"present": has_email, "points": email_pts, "max": 5}

    # ── Phone present ─────────────────────────────────────────────────────────
    has_phone       = bool(re.search(r'(\+?\d[\d\s\-().]{8,14}\d)', resume_text))
    phone_pts       = 5 if has_phone else 0
    total          += phone_pts
    details["phone"] = {"present": has_phone, "points": phone_pts, "max": 5}

    # ── Word count in ideal range ─────────────────────────────────────────────
    word_count      = len(resume_text.split())
    good_length     = 300 <= word_count <= 1000
    length_pts      = 5 if good_length else (3 if word_count > 150 else 0)
    total          += length_pts
    details["length"] = {
        "word_count": word_count,
        "ideal"     : good_length,
        "points"    : length_pts,
        "max"       : 5
    }

    # ── Action verbs ──────────────────────────────────────────────────────────
    action_verbs    = [
        "developed", "built", "designed", "implemented", "led", "managed",
        "created", "improved", "increased", "reduced", "launched", "delivered",
        "collaborated", "architected", "optimized", "automated", "deployed",
        "analyzed", "researched", "trained", "mentored", "streamlined"
    ]
    text_lower      = resume_text.lower()
    verbs_found     = [v for v in action_verbs if v in text_lower]
    verb_pts        = 5 if len(verbs_found) >= 3 else (3 if len(verbs_found) >= 1 else 0)
    total          += verb_pts
    details["action_verbs"] = {
        "found" : verbs_found,
        "points": verb_pts,
        "max"   : 5
    }

    return {
        "score"  : total,
        "max"    : 20,
        "details": details
    }


# ──────────────────────────────────────────────────────────────────────────────
# FUNCTION 4: Score skills coverage
# ──────────────────────────────────────────────────────────────────────────────
def score_skills(resume_skills: list, job_text: str) -> dict:
    """
    Score how many job-relevant skills appear in the resume.

    Max score: 20 points

    Args:
        resume_skills: List of skills extracted by ner.extract_skills()
        job_text     : Job description text

    Returns:
        {"score": int, "max": 20, "details": str}
    """
    if not resume_skills:
        return {"score": 0, "max": 20, "details": "No skills found in resume"}

    job_lower       = job_text.lower()
    matched_skills  = [s for s in resume_skills if s.lower() in job_lower]
    match_ratio     = len(matched_skills) / max(len(resume_skills), 1)

    points          = round(match_ratio * 20)

    return {
        "score"          : points,
        "max"            : 20,
        "matched_skills" : matched_skills,
        "details"        : f"{len(matched_skills)} of {len(resume_skills)} resume skills match the job"
    }


# ──────────────────────────────────────────────────────────────────────────────
# FUNCTION 5: Get total ATS score
# ──────────────────────────────────────────────────────────────────────────────
def get_total_score(resume_text: str, job_text: str, sections: dict, resume_skills: list) -> dict:
    """
    Compute full ATS score out of 100.

    Breakdown:
        - Keywords  : 35 points
        - Sections  : 25 points
        - Format    : 20 points
        - Skills    : 20 points

    Args:
        resume_text  : Raw resume text
        job_text     : Job description text
        sections     : Output of ner.extract_sections()
        resume_skills: Output of ner.extract_skills()

    Returns:
        {
            "total_score"    : int (out of 100),
            "grade"          : str ("Excellent" / "Good" / "Fair" / "Poor"),
            "keyword_score"  : dict,
            "section_score"  : dict,
            "format_score"   : dict,
            "skills_score"   : dict
        }
    """
    keyword_result  = score_keywords(resume_text, job_text)
    section_result  = score_sections(sections)
    format_result   = score_format(resume_text)
    skills_result   = score_skills(resume_skills, job_text)

    total = (
        keyword_result["score"] +
        section_result["score"] +
        format_result["score"]  +
        skills_result["score"]
    )

    # Grade based on total score
    if total >= 80:
        grade = "Excellent"
    elif total >= 60:
        grade = "Good"
    elif total >= 40:
        grade = "Fair"
    else:
        grade = "Poor"

    return {
        "total_score"   : total,
        "grade"         : grade,
        "keyword_score" : keyword_result,
        "section_score" : section_result,
        "format_score"  : format_result,
        "skills_score"  : skills_result
    }


# ──────────────────────────────────────────────────────────────────────────────
# Local test — run: python -m analyzer.scorer
# ──────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import os, sys
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    ROOT     = os.path.abspath(os.path.join(BASE_DIR, ".."))
    sys.path.insert(0, ROOT)

    from analyzer.parser import extract_text_from_pdf
    from analyzer.ner    import extract_sections, extract_skills

    pdf_path    = os.path.join(ROOT, "sample_resume.pdf")
    resume_text = extract_text_from_pdf(pdf_path)

    job_text = """
    Looking for a Python developer with experience in machine learning,
    TensorFlow, data analysis, SQL, and cloud platforms like AWS.
    Strong communication and teamwork skills required.
    """

    sections        = extract_sections(resume_text)
    resume_skills   = extract_skills(resume_text)
    result          = get_total_score(resume_text, job_text, sections, resume_skills)

    print(f"Total ATS Score : {result['total_score']} / 100")
    print(f"Grade           : {result['grade']}")
    print(f"Keyword Score   : {result['keyword_score']['score']} / 35")
    print(f"Section Score   : {result['section_score']['score']} / 25")
    print(f"Format Score    : {result['format_score']['score']} / 20")
    print(f"Skills Score    : {result['skills_score']['score']} / 20")