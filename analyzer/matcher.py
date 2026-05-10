import json
import os

# ── Path to job descriptions ───────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
JOBS_PATH = os.path.join(BASE_DIR, "..", "data", "job_descriptions.json")


# ──────────────────────────────────────────────────────────────────────────────
# HELPER: Load job descriptions from JSON
# ──────────────────────────────────────────────────────────────────────────────
def load_job_descriptions() -> list:
    """
    Load job descriptions from job_descriptions.json.

    Returns:
        List of job dicts:
        [
            {
                "title": "Python Developer",
                "company": "Google",
                "description": "We are looking for..."
            },
            ...
        ]
    """
    with open(JOBS_PATH, "r", encoding="utf-8") as f:
        jobs = json.load(f)
    return jobs


# ──────────────────────────────────────────────────────────────────────────────
# FUNCTION 1: Match resume against a single job description
# ──────────────────────────────────────────────────────────────────────────────
def match_single_job(resume_text, job_description):
    from analyzer.vectorizer import get_combined_score   # import here
    return get_combined_score(resume_text, job_description)
    """
    Compute similarity between a resume and one job description.

    Args:
        resume_text     : Raw resume text
        job_description : Job description text

    Returns:
        Dictionary with tfidf, bert and combined scores
    """
    return get_combined_score(resume_text, job_description)


# ──────────────────────────────────────────────────────────────────────────────
# FUNCTION 2: Match resume against all jobs in job_descriptions.json
# ──────────────────────────────────────────────────────────────────────────────
def match_with_all_jobs(resume_text):
    from analyzer.vectorizer import get_combined_score 
    """
    Match resume against all job descriptions and return ranked results.

    Args:
        resume_text: Raw resume text

    Returns:
        List of job match results sorted by combined_score descending:
        [
            {
                "title": "Python Developer",
                "company": "Google",
                "description": "...",
                "tfidf_score": 0.42,
                "bert_score": 0.81,
                "combined_score": 0.74,
                "match_percent": 74.0
            },
            ...
        ]
    """
    jobs    = load_job_descriptions()
    results = []

    for job in jobs:
        scores = get_combined_score(resume_text, job["description"])

        results.append({
            "title"          : job.get("title", "Unknown"),
            "company"        : job.get("company", "Unknown"),
            "description"    : job.get("description", ""),
            "tfidf_score"    : scores["tfidf_score"],
            "bert_score"     : scores["bert_score"],
            "combined_score" : scores["combined_score"],
            "match_percent"  : round(scores["combined_score"] * 100, 1)
        })

    # Sort by combined_score descending — best match first
    results.sort(key=lambda x: x["combined_score"], reverse=True)

    return results


# ──────────────────────────────────────────────────────────────────────────────
# FUNCTION 3: Get top N matches
# ──────────────────────────────────────────────────────────────────────────────
def get_top_matches(resume_text: str, top_n: int = 5) -> list:
    """
    Return only the top N job matches for the resume.

    Args:
        resume_text: Raw resume text
        top_n      : Number of top results to return (default 5)

    Returns:
        List of top N job match dicts (same format as match_with_all_jobs)
    """
    all_matches = match_with_all_jobs(resume_text)
    return all_matches[:top_n]


# ──────────────────────────────────────────────────────────────────────────────
# Local test — run: python -m analyzer.matcher
# ──────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import sys
    ROOT = os.path.abspath(os.path.join(BASE_DIR, ".."))
    sys.path.insert(0, ROOT)

    from analyzer.parser import extract_text_from_pdf

    pdf_path = os.path.join(ROOT, "sample_resume.pdf")
    resume_text = extract_text_from_pdf(pdf_path)

    print("Matching resume against all jobs...\n")
    top = get_top_matches(resume_text, top_n=3)

    for i, job in enumerate(top, 1):
        print(f"#{i} {job['title']} at {job['company']}")
        print(f"   Match: {job['match_percent']}%")
        print(f"   TF-IDF: {job['tfidf_score']} | BERT: {job['bert_score']}")
        print()