import re


def score_keywords(resume_text: str, job_text: str) -> dict:
    from analyzer.vectorizer import get_tfidf_similarity
    similarity = get_tfidf_similarity(resume_text, job_text)
    points     = round(similarity * 35)
    return {
        "score"  : points,
        "max"    : 35,
        "details": f"Keyword overlap similarity: {round(similarity * 100, 1)}%"
    }


def score_sections(sections: dict) -> dict:
    section_weights = {
        "experience" : 8,
        "education"  : 7,
        "skills"     : 5,
        "summary"    : 3,
        "projects"   : 2,
    }
    details = {}
    total   = 0

    for section, weight in section_weights.items():
        present          = sections.get(section, False)
        earned           = weight if present else 0
        total           += earned
        details[section] = {"present": present, "points": earned, "max": weight}

    return {"score": total, "max": 25, "details": details}


def score_format(resume_text: str) -> dict:
    details = {}
    total   = 0

    has_email  = bool(re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', resume_text))
    email_pts  = 5 if has_email else 0
    total     += email_pts
    details["email"] = {"present": has_email, "points": email_pts, "max": 5}

    has_phone  = bool(re.search(r'(\+?\d[\d\s\-().]{8,14}\d)', resume_text))
    phone_pts  = 5 if has_phone else 0
    total     += phone_pts
    details["phone"] = {"present": has_phone, "points": phone_pts, "max": 5}

    word_count   = len(resume_text.split())
    good_length  = 300 <= word_count <= 1000
    length_pts   = 5 if good_length else (3 if word_count > 150 else 0)
    total       += length_pts
    details["length"] = {"word_count": word_count, "ideal": good_length, "points": length_pts, "max": 5}

    action_verbs = [
        "developed", "built", "designed", "implemented", "led", "managed",
        "created", "improved", "increased", "reduced", "launched", "delivered",
        "collaborated", "architected", "optimized", "automated", "deployed",
        "analyzed", "researched", "trained", "mentored", "streamlined"
    ]
    text_lower   = resume_text.lower()
    verbs_found  = [v for v in action_verbs if v in text_lower]
    verb_pts     = 5 if len(verbs_found) >= 3 else (3 if len(verbs_found) >= 1 else 0)
    total       += verb_pts
    details["action_verbs"] = {"found": verbs_found, "points": verb_pts, "max": 5}

    return {"score": total, "max": 20, "details": details}


def score_skills(resume_skills: list, job_text: str) -> dict:
    if not resume_skills:
        return {"score": 0, "max": 20, "details": "No skills found in resume"}

    job_lower      = job_text.lower()
    matched_skills = [s for s in resume_skills if s.lower() in job_lower]
    match_ratio    = len(matched_skills) / max(len(resume_skills), 1)
    points         = round(match_ratio * 20)

    return {
        "score"         : points,
        "max"           : 20,
        "matched_skills": matched_skills,
        "details"       : f"{len(matched_skills)} of {len(resume_skills)} resume skills match the job"
    }


def get_total_score(resume_text: str, job_text: str, sections: dict, resume_skills: list) -> dict:
    keyword_result = score_keywords(resume_text, job_text)
    section_result = score_sections(sections)
    format_result  = score_format(resume_text)
    skills_result  = score_skills(resume_skills, job_text)

    total = (
        keyword_result["score"] +
        section_result["score"] +
        format_result["score"]  +
        skills_result["score"]
    )

    if total >= 80:
        grade = "Excellent"
    elif total >= 60:
        grade = "Good"
    elif total >= 40:
        grade = "Fair"
    else:
        grade = "Poor"

    return {
        "total_score"  : total,
        "grade"        : grade,
        "keyword_score": keyword_result,
        "section_score": section_result,
        "format_score" : format_result,
        "skills_score" : skills_result
    }


if __name__ == "__main__":
    import os, sys
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    ROOT     = os.path.abspath(os.path.join(BASE_DIR, ".."))
    sys.path.insert(0, ROOT)

    from analyzer.parser import extract_text_from_pdf
    from analyzer.ner    import extract_sections, extract_skills

    pdf_path      = os.path.join(ROOT, "sample_resume.pdf")
    resume_text   = extract_text_from_pdf(pdf_path)
    job_text      = "Python developer with machine learning, TensorFlow, SQL, AWS experience."
    sections      = extract_sections(resume_text)
    resume_skills = extract_skills(resume_text)
    result        = get_total_score(resume_text, job_text, sections, resume_skills)

    print(f"Total ATS Score : {result['total_score']} / 100")
    print(f"Grade           : {result['grade']}")