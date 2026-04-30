import re
import os


# ──────────────────────────────────────────────────────────────────────────────
# FUNCTION 1: Get missing keywords from job description
# ──────────────────────────────────────────────────────────────────────────────
def get_missing_keywords(resume_text: str, job_text: str) -> list:
    """
    Find important words in the job description that are missing from the resume.

    Strategy:
    - Tokenize job description into meaningful words
    - Filter out stop words and short words
    - Check which ones are absent from the resume

    Args:
        resume_text: Raw resume text
        job_text   : Job description text

    Returns:
        List of missing keyword strings
    """
    # Common stop words to ignore
    stop_words = {
        "the", "and", "for", "with", "that", "this", "have", "will",
        "are", "you", "our", "your", "from", "they", "been", "their",
        "has", "not", "but", "what", "all", "were", "when", "we",
        "there", "can", "an", "or", "do", "if", "in", "of", "to",
        "a", "is", "as", "at", "be", "by", "on", "it", "its"
    }

    # Tokenize job description — only meaningful words (length > 3)
    job_words = re.findall(r'\b[a-zA-Z][a-zA-Z+#.]*\b', job_text)
    job_words = [
        w for w in job_words
        if w.lower() not in stop_words and len(w) > 3
    ]

    # Remove duplicates while preserving order
    seen      = set()
    job_words = [w for w in job_words if not (w.lower() in seen or seen.add(w.lower()))]

    resume_lower = resume_text.lower()

    # Find words from job that are NOT in the resume
    missing = [
        word for word in job_words
        if word.lower() not in resume_lower
    ]

    return missing


# ──────────────────────────────────────────────────────────────────────────────
# FUNCTION 2: Get missing skills specifically
# ──────────────────────────────────────────────────────────────────────────────
def get_missing_skills(resume_skills: list, job_text: str, all_skills: list) -> list:
    """
    Find skills mentioned in the job description that the resume is missing.

    Args:
        resume_skills: Skills already found in resume (from ner.extract_skills)
        job_text     : Job description text
        all_skills   : Full skills list (from ner.load_skills)

    Returns:
        List of missing skill strings
    """
    job_lower        = job_text.lower()
    resume_lower_set = {s.lower() for s in resume_skills}

    missing_skills = [
        skill for skill in all_skills
        if skill.lower() in job_lower
        and skill.lower() not in resume_lower_set
    ]

    return missing_skills


# ──────────────────────────────────────────────────────────────────────────────
# FUNCTION 3: Generate human-readable improvement suggestions
# ──────────────────────────────────────────────────────────────────────────────
def generate_suggestions(
    resume_text   : str,
    job_text      : str,
    sections      : dict,
    resume_skills : list,
    format_score  : dict,
    total_score   : int
) -> list:
    """
    Generate a prioritized list of improvement suggestions.

    Args:
        resume_text  : Raw resume text
        job_text     : Job description text
        sections     : Output of ner.extract_sections()
        resume_skills: Output of ner.extract_skills()
        format_score : Output of scorer.score_format()
        total_score  : Total ATS score out of 100

    Returns:
        List of suggestion strings, ordered by priority
    """
    suggestions = []

    # ── Missing sections ───────────────────────────────────────────────────────
    important_sections = {
        "summary"   : "Add a professional Summary or Objective section at the top of your resume.",
        "experience": "Add a Work Experience section with your job history.",
        "education" : "Add an Education section with your degrees and institutions.",
        "skills"    : "Add a dedicated Skills section listing your technical and soft skills.",
        "projects"  : "Add a Projects section to showcase your practical work.",
    }

    for section, suggestion in important_sections.items():
        if not sections.get(section, False):
            suggestions.append(f"⚠️  {suggestion}")

    # ── Missing contact info ───────────────────────────────────────────────────
    format_details = format_score.get("details", {})

    if not format_details.get("email", {}).get("present", True):
        suggestions.append("⚠️  Add your email address — it's missing from the resume.")

    if not format_details.get("phone", {}).get("present", True):
        suggestions.append("⚠️  Add your phone number — it's missing from the resume.")

    # ── Word count feedback ────────────────────────────────────────────────────
    word_count = format_details.get("length", {}).get("word_count", 0)
    if word_count < 300:
        suggestions.append(
            f"📝  Your resume is too short ({word_count} words). "
            "Aim for 300-700 words with more detail in your experience and projects."
        )
    elif word_count > 1000:
        suggestions.append(
            f"✂️  Your resume is quite long ({word_count} words). "
            "Try to keep it concise — 1 page is ideal for most roles."
        )

    # ── Action verbs ──────────────────────────────────────────────────────────
    verbs_found = format_details.get("action_verbs", {}).get("found", [])
    if len(verbs_found) < 3:
        suggestions.append(
            "💡  Use more action verbs in your experience section. "
            "Examples: Developed, Built, Led, Improved, Implemented, Delivered."
        )

    # ── Missing skills ─────────────────────────────────────────────────────────
    from analyzer.ner import load_skills
    all_skills     = load_skills()
    missing_skills = get_missing_skills(resume_skills, job_text, all_skills)

    if missing_skills:
        top_missing = missing_skills[:8]        # show max 8 missing skills
        suggestions.append(
            f"🔧  Add these in-demand skills that appear in the job description: "
            f"{', '.join(top_missing)}."
        )

    # ── Quantified achievements ────────────────────────────────────────────────
    has_numbers = bool(re.search(r'\d+%|\d+x|\$\d+|\d+ (users|customers|projects|teams)', resume_text))
    if not has_numbers:
        suggestions.append(
            "📊  Quantify your achievements. "
            "For example: 'Improved performance by 30%' or 'Led a team of 5 engineers'."
        )

    # ── Overall score feedback ─────────────────────────────────────────────────
    if total_score < 40:
        suggestions.append(
            "🚨  Your ATS score is low. Focus on adding missing sections, "
            "matching job keywords, and including relevant skills first."
        )
    elif total_score < 60:
        suggestions.append(
            "📈  Your resume is decent but needs improvement. "
            "Focus on tailoring keywords to match the job description."
        )
    elif total_score >= 80:
        suggestions.append(
            "✅  Great resume! Just make sure to tailor it slightly for each job application."
        )

    return suggestions


# ──────────────────────────────────────────────────────────────────────────────
# FUNCTION 4: Full suggestion report (main entry point)
# ──────────────────────────────────────────────────────────────────────────────
def get_improvement_report(
    resume_text   : str,
    job_text      : str,
    sections      : dict,
    resume_skills : list,
    format_score  : dict,
    total_score   : int
) -> dict:
    """
    Generate a complete improvement report combining keyword gaps and suggestions.

    Returns:
        {
            "missing_keywords": [str, ...],
            "missing_skills"  : [str, ...],
            "suggestions"     : [str, ...]
        }
    """
    from analyzer.ner import load_skills
    all_skills = load_skills()

    return {
        "missing_keywords": get_missing_keywords(resume_text, job_text),
        "missing_skills"  : get_missing_skills(resume_skills, job_text, all_skills),
        "suggestions"     : generate_suggestions(
            resume_text, job_text, sections,
            resume_skills, format_score, total_score
        )
    }


# ──────────────────────────────────────────────────────────────────────────────
# Local test — run: python -m analyzer.suggester
# ──────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import sys
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    ROOT     = os.path.abspath(os.path.join(BASE_DIR, ".."))
    sys.path.insert(0, ROOT)

    from analyzer.parser  import extract_text_from_pdf
    from analyzer.ner     import extract_sections, extract_skills
    from analyzer.scorer  import get_total_score, score_format

    pdf_path    = os.path.join(ROOT, "sample_resume.pdf")
    resume_text = extract_text_from_pdf(pdf_path)

    job_text = """
    Looking for a Python developer with experience in machine learning,
    TensorFlow, Docker, AWS, and REST APIs.
    Strong communication and leadership skills required.
    """

    sections        = extract_sections(resume_text)
    resume_skills   = extract_skills(resume_text)
    score_result    = get_total_score(resume_text, job_text, sections, resume_skills)
    format_result   = score_result["format_score"]

    report = get_improvement_report(
        resume_text, job_text, sections,
        resume_skills, format_result, score_result["total_score"]
    )

    print("===== MISSING SKILLS =====")
    print(report["missing_skills"])

    print("\n===== SUGGESTIONS =====")
    for s in report["suggestions"]:
        print(s)