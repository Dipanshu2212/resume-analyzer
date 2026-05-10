import json
import os

BASE_DIR  = os.path.dirname(os.path.abspath(__file__))
ROOT      = os.path.abspath(os.path.join(BASE_DIR, ".."))
JOBS_PATH = os.path.join(ROOT, "data", "job_descriptions.json")


def load_job_descriptions() -> list:
    with open(JOBS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def match_single_job(resume_text: str, job_description: str) -> dict:
    from analyzer.vectorizer import get_combined_score
    return get_combined_score(resume_text, job_description)


def match_with_all_jobs(resume_text: str) -> list:
    from analyzer.vectorizer import get_combined_score

    jobs    = load_job_descriptions()
    results = []

    for job in jobs:
        scores = get_combined_score(resume_text, job["description"])
        results.append({
            "title"         : job.get("title", "Unknown"),
            "company"       : job.get("company", "Unknown"),
            "description"   : job.get("description", ""),
            "tfidf_score"   : scores["tfidf_score"],
            "bert_score"    : scores["bert_score"],
            "combined_score": scores["combined_score"],
            "match_percent" : round(scores["combined_score"] * 100, 1)
        })

    results.sort(key=lambda x: x["combined_score"], reverse=True)
    return results


def get_top_matches(resume_text: str, top_n: int = 5) -> list:
    return match_with_all_jobs(resume_text)[:top_n]


if __name__ == "__main__":
    import sys
    sys.path.insert(0, ROOT)

    from analyzer.parser import extract_text_from_pdf

    pdf_path    = os.path.join(ROOT, "sample_resume.pdf")
    resume_text = extract_text_from_pdf(pdf_path)
    top         = get_top_matches(resume_text, top_n=3)

    for i, job in enumerate(top, 1):
        print(f"#{i} {job['title']} at {job['company']}")
        print(f"   Match: {job['match_percent']}%")
        print()