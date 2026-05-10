import re
import json
import os

# ── Load spaCy model once at module level ──────────────────────────────────────
import spacy

try:
    nlp = spacy.load("en_core_web_lg")
except OSError:
    try:
        nlp = spacy.load("en_core_web_md")
    except OSError:
        raise OSError("Run: python -m spacy download en_core_web_md")

# ── Paths ──────────────────────────────────────────────────────────────────────
BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
SKILLS_PATH = os.path.join(BASE_DIR, "..", "data", "skills_list.json")

# ── Blocklist — words spaCy wrongly calls ORG ─────────────────────────────────
ORG_BLOCKLIST = {
    "education", "experience", "skills", "projects", "objective",
    "summary", "certifications", "achievements", "hobbies",
    "interests", "references", "profile", "gpa",
    "python", "java", "javascript", "typescript", "css", "html",
    "sql", "bash", "react", "node", "nodejs", "django", "flask",
    "numpy", "pandas", "matplotlib", "tensorflow", "pytorch",
    "scikit", "scikit-learn", "opencv", "spacy", "nltk",
    "docker", "kubernetes", "git", "github", "linux", "aws",
    "azure", "gcp", "mysql", "postgresql", "mongodb", "redis",
    "machine learning enthusiast", "aspiring", "personal project",
    "full stack", "frontend", "backend", "ui", "ux", "api",
    "rest", "agile", "scrum", "kociemba", "rubik", "cbse",
    "intermediate", "senior", "junior", "intern", "developer",
    "engineer", "analyst", "manager", "lead", "head", "computer science and engineering",
    "technical group", "cultural heritage of india", "personal project", "solutions architecture simulation",
    "certificate", "certification", "hackathon 2024 certificate", "apac",
}

# ── Known organizations ────────────────────────────────────────────────────────
KNOWN_ORGS = [
    "IIT", "NIT", "BITS", "IIM", "VIT", "SRM", "Amity",
    "Maharana Pratap Group of Institutes", "Delhi University",
    "Jawaharlal Nehru University", "Anna University",
    "Google", "Microsoft", "Amazon", "Apple", "Meta", "Netflix",
    "Infosys", "Wipro", "TCS", "Tata Consultancy Services",
    "HCL", "Cognizant", "Accenture", "IBM", "Oracle", "Capgemini",
    "Tech Mahindra", "Flipkart", "Zomato", "Swiggy", "Paytm",
    "Tech-E-Clan", "IEEE", "ACM", "NSS", "NCC",
    "Smart India Hackathon", "GDSC",
]

# After building organizations list, remove substrings
def remove_substrings(org_list):
    result = []
    for org in org_list:
        # Only add if no other org in the list contains this one
        if not any(
            org != other and org.lower() in other.lower()
            for other in org_list
        ):
            result.append(org)
    return result

def load_skills() -> list:
    with open(SKILLS_PATH, "r", encoding="utf-8") as f:
        skills_dict = json.load(f)
    flat_skills = []
    for category, skills in skills_dict.items():
        flat_skills.extend(skills)
    return flat_skills


def extract_entities(text: str) -> dict:
    doc = nlp(text)

    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    emails = re.findall(email_pattern, text)
    email  = emails[0] if emails else None

    phone_pattern = r'(\+?\d[\d\s\-().]{8,14}\d)'
    phones = re.findall(phone_pattern, text)
    phone  = phones[0].strip() if phones else None

    name = None
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            name = ent.text
            break

    organizations = []
    text_lower    = text.lower()

    for org in KNOWN_ORGS:
        if org.lower() in text_lower and org not in organizations:
            organizations.append(org)

    for ent in doc.ents:
        if ent.label_ == "ORG":
            clean = ent.text.strip()

            # Remove bullet points and special characters from start
            clean = clean.lstrip("•●▪-– ")

            if (
                clean.lower() not in ORG_BLOCKLIST
                and len(clean) > 4
                and clean not in organizations
                and not clean.isupper()
                and sum(1 for c in clean if c.isupper()) < len(clean) * 0.7
                and "•" not in clean          # ← skip fragments with bullet points
                and "certificate" not in clean.lower()   # ← skip certifications
                and "simulation" not in clean.lower()    # ← skip simulation titles
                and "project" not in clean.lower()       # ← skip project names
            ):
                organizations.append(clean)
                
    organizations = remove_substrings(organizations)
    return {
        "name"         : name,
        "email"        : email,
        "phone"        : phone,
        "organizations": organizations
    }


def extract_skills(text: str) -> list:
    skills     = load_skills()
    text_lower = text.lower()
    found      = []

    for skill in skills:
        pattern = r'\b' + re.escape(skill.lower()) + r'\b'
        if re.search(pattern, text_lower):
            if skill not in found:
                found.append(skill)

    return found


def extract_sections(text: str) -> dict:
    text_lower = text.lower()
    return {
        "education"     : bool(re.search(r'\beducation\b', text_lower)),
        "experience"    : bool(re.search(r'\bexperience\b|\bwork history\b', text_lower)),
        "skills"        : bool(re.search(r'\bskills\b|\btechnical skills\b', text_lower)),
        "projects"      : bool(re.search(r'\bprojects\b|\bproject\b', text_lower)),
        "summary"       : bool(re.search(r'\bsummary\b|\bobjective\b|\bprofile\b', text_lower)),
        "certifications": bool(re.search(r'\bcertification\b|\bcertifications\b|\bcourses\b', text_lower)),
        "achievements"  : bool(re.search(r'\bachievement\b|\bawards\b|\bhonors\b', text_lower)),
    }


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
        "raw_text"      : text
    }


if __name__ == "__main__":
    import sys
    ROOT = os.path.abspath(os.path.join(BASE_DIR, ".."))
    sys.path.insert(0, ROOT)

    from analyzer.parser import extract_text_from_pdf

    pdf_path = os.path.join(ROOT, "sample_resume.pdf")
    text     = extract_text_from_pdf(pdf_path)
    result   = analyze_resume(text)

    print(f"Name          : {result['name']}")
    print(f"Email         : {result['email']}")
    print(f"Phone         : {result['phone']}")
    print(f"Organizations : {result['organizations']}")
    print(f"Skills found  : {result['skills']}")
    print(f"\nSections:")
    for s, present in result["sections"].items():
        print(f"  {'✓' if present else '✗'} {s.capitalize()}")