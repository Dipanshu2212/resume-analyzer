import re
import json
import os

KNOWN_ORGS = [
    # Colleges & Universities
    "IIT", "NIT", "BITS", "IIM", "VIT", "SRM", "Amity",
    "Maharana Pratap Group of Institutes", "Delhi University",
    "Jawaharlal Nehru University", "Anna University",

    # Companies
    "Google", "Microsoft", "Amazon", "Apple", "Meta", "Netflix",
    "Infosys", "Wipro", "TCS", "Tata Consultancy Services",
    "HCL", "Cognizant", "Accenture", "IBM", "Oracle", "Capgemini",
    "Tech Mahindra", "Flipkart", "Zomato", "Swiggy", "Paytm",
    "Razorpay", "BYJU'S", "Ola", "Uber", "LinkedIn", "Twitter",

    # Clubs & Organizations
    "Tech-E-Clan", "IEEE", "ACM", "NSS", "NCC",
    "Smart India Hackathon", "Google Developer Student Clubs",
    "GDSC", "Microsoft Learn Student Ambassadors",
]

# Words that spaCy wrongly calls ORG — block these completely
ORG_BLOCKLIST = {
    # Section headers
    "education", "experience", "skills", "projects", "objective",
    "summary", "certifications", "achievements", "hobbies",
    "interests", "references", "profile", "gpa",

    # Programming languages and tools
    "python", "java", "javascript", "typescript", "css", "html",
    "sql", "bash", "react", "node", "nodejs", "django", "flask",
    "numpy", "pandas", "matplotlib", "tensorflow", "pytorch",
    "scikit", "scikit-learn", "opencv", "spacy", "nltk",
    "docker", "kubernetes", "git", "github", "linux", "aws",
    "azure", "gcp", "mysql", "postgresql", "mongodb", "redis",

    # Common resume words wrongly flagged
    "machine learning enthusiast", "aspiring", "personal project",
    "full stack", "frontend", "backend", "ui", "ux", "api",
    "rest", "agile", "scrum", "kociemba", "rubik", "cbse",
    "intermediate", "senior", "junior", "intern", "developer",
    "engineer", "analyst", "manager", "lead", "head",
}

def get_nlp():
    import spacy                          # import inside function
    try:
        return spacy.load("en_core_web_md")
    except OSError:
        raise OSError("spaCy model not found. Run: python -m spacy download en_core_web_md")



BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SKILLS_PATH = os.path.join(BASE_DIR, "..", "data", "skills_list.json")


def load_skills() -> list:
    with open(SKILLS_PATH, "r", encoding="utf-8") as f:
        skills_dict = json.load(f)

    flat_skills = []
    for category, skills in skills_dict.items():
        flat_skills.extend(skills)

    return flat_skills


def extract_entities(text: str) -> dict:
    """
    Extract structured entities from resume text.
    - spaCy used ONLY for PERSON detection
    - ORG detection done via curated list + spaCy as fallback
    - Regex for email and phone
    """
    nlp = get_nlp()
    doc = nlp(text)

    # ── Email ──────────────────────────────────────────────────────────────
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    emails = re.findall(email_pattern, text)
    email  = emails[0] if emails else None

    # ── Phone ──────────────────────────────────────────────────────────────
    phone_pattern = r'(\+?\d[\d\s\-().]{8,14}\d)'
    phones = re.findall(phone_pattern, text)
    phone  = phones[0].strip() if phones else None

    # ── Name — spaCy is reliable for PERSON ────────────────────────────────
    name = None
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            name = ent.text
            break

    # ── Organizations — hybrid approach ────────────────────────────────────
    organizations = []

    # Step 1: Check known orgs list first (most reliable)
    text_lower = text.lower()
    for org in KNOWN_ORGS:
        if org.lower() in text_lower and org not in organizations:
            organizations.append(org)

    # Step 2: Add spaCy ORGs only if they pass the blocklist filter
    for ent in doc.ents:
        if ent.label_ == "ORG":
            clean = ent.text.strip()
            if (
                clean.lower() not in ORG_BLOCKLIST   # not in blocklist
                and len(clean) > 4                    # not a short abbreviation
                and clean not in organizations        # not already added
                and not clean.isupper()              # skip ALL CAPS abbreviations like CSS, JS
                and sum(1 for c in clean if c.isupper()) < len(clean) * 0.7  # skip mostly-caps
            ):
                organizations.append(clean)

    return {
        "name"         : name,
        "email"        : email,
        "phone"        : phone,
        "organizations": organizations
    }

def extract_skills(text: str) -> list:
    skills = load_skills()
    text_lower = text.lower()

    found_skills = []

    for skill in skills:
        pattern = r'\b' + re.escape(skill.lower()) + r'\b'
        if re.search(pattern, text_lower):
            if skill not in found_skills:       # avoid duplicates
                found_skills.append(skill)

    return found_skills

def extract_sections(text: str) -> dict:
    text_lower = text.lower()

    sections = {
        "education"  : bool(re.search(r'\beducation\b', text_lower)),
        "experience" : bool(re.search(r'\bexperience\b|\bwork history\b', text_lower)),
        "skills"     : bool(re.search(r'\bskills\b|\btechnical skills\b', text_lower)),
        "projects"   : bool(re.search(r'\bprojects\b|\bproject\b', text_lower)),
        "summary"    : bool(re.search(r'\bsummary\b|\bobjective\b|\bprofile\b', text_lower)),
        "certifications": bool(re.search(r'\bcertification\b|\bcertifications\b|\bcourses\b', text_lower)),
        "achievements": bool(re.search(r'\bachievement\b|\bawards\b|\bhonors\b', text_lower)),
    }

    return sections


def analyze_resume(text: str) -> dict:
    entities = extract_entities(text)
    skills   = extract_skills(text)
    sections = extract_sections(text)

    return {
        "name"          : entities["name"],
        "email"         : entities["email"],
        "phone"         : entities["phone"],
        "organizations" : entities["organizations"],
        "skills"        : skills,
        "sections"      : sections,
        "raw_text"      : text              # pass through for downstream modules
    }


if __name__ == "__main__":
    import sys

    # Add the root resume_analyzer/ folder to Python path
    ROOT = os.path.abspath(os.path.join(BASE_DIR, ".."))
    sys.path.insert(0, ROOT)

    from analyzer.parser import extract_text_from_pdf

    pdf_path = os.path.join(ROOT, "sample_resume.pdf")

    print("Extracting text from resume...")
    text = extract_text_from_pdf(pdf_path)

    print("Analyzing resume...\n")
    result = analyze_resume(text)

    print(f"Name          : {result['name']}")
    print(f"Email         : {result['email']}")
    print(f"Phone         : {result['phone']}")
    print(f"Organizations : {result['organizations']}")
    print(f"Skills found  : {result['skills']}")
    print(f"\nSections detected:")
    for section, present in result["sections"].items():
        status = "✓" if present else "✗"
        print(f"  {status} {section.capitalize()}")