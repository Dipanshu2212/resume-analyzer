import re
import json
import os

# ── Load spaCy model once at module level ──────────────────────────────────────
import spacy

try:
    nlp = spacy.load("C:/Users/dipan/OneDrive/Desktop/Trained/en_core_web_lg")
except OSError:
    try:
        nlp = spacy.load("en_core_web_lg")
    except OSError:
        nlp = spacy.load("en_core_web_md")
        raise OSError("Fine-tuned model not found, loading default")

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
    # ── Indian Colleges ────────────────────────────────────────────────────
    "IIT Bombay", "IIT Delhi", "IIT Madras", "IIT Kanpur", "IIT Kharagpur",
    "IIT Roorkee", "IIT Guwahati", "IIT Hyderabad", "IIT BHU",
    "NIT Trichy", "NIT Surathkal", "NIT Warangal", "NIT Calicut",
    "BITS Pilani", "BITS Goa", "BITS Hyderabad",
    "VIT Vellore", "VIT Chennai",           # ← "VIT" with city to avoid "Vite" clash
    "SRM University", "Amity University",
    "Delhi University", "Mumbai University", "Anna University",
    "Jawaharlal Nehru University", "Jadavpur University",
    "Maharana Pratap Group of Institutes",
    "Maharana Institute of Professional Studies Kanpur",
    "Kendriya Vidyalaya O.E.F Kanpur",
    "Dr. Virendra Swarup Public School",

    # ── Global Companies ───────────────────────────────────────────────────
    "Google", "Microsoft", "Amazon", "Apple", "Meta", "Netflix",
    "Adobe", "Salesforce", "Oracle", "IBM", "Intel", "Nvidia",
    "Twitter", "LinkedIn", "Uber", "Airbnb", "Spotify",

    # ── Indian Companies ───────────────────────────────────────────────────
    "Infosys", "Wipro", "TCS", "Tata Consultancy Services",
    "HCL Technologies", "Tech Mahindra", "Cognizant", "Accenture",
    "Capgemini", "Mphasis", "Hexaware", "Mindtree",
    "Flipkart", "Zomato", "Swiggy", "Paytm", "Razorpay",
    "BYJU'S", "Ola", "Myntra", "Meesho", "PhonePe",

    # ── Clubs & Organizations ──────────────────────────────────────────────
    "Tech-E-Clan", "IEEE", "ACM", "NSS", "NCC",
    "Smart India Hackathon",
    "Google Developer Student Clubs", "GDSC",
    "Microsoft Learn Student Ambassadors",

    # ── Platforms with ORG context ─────────────────────────────────────────
    "HackerRank", "LeetCode", "Coursera", "Udemy", "edX",
    "GitHub", "GitLab",
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
    doc  = nlp(text)

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

    # ── Organizations — whitelist ONLY, no spaCy guessing ──────────────────
    organizations = extract_organizations(text)

    return {
        "name"         : name,
        "email"        : email,
        "phone"        : phone,
        "organizations": organizations
    }


def extract_organizations(text: str) -> list:
    """
    Detect organizations using whitelist matching with word boundaries.
    Prevents substring matches like 'Ola' matching inside 'Solar'.
    """
    organizations = []

    for org in KNOWN_ORGS:
        # Use word boundary regex to prevent partial matches
        pattern = r'\b' + re.escape(org) + r'\b'
        if re.search(pattern, text, re.IGNORECASE):
            if org not in organizations:
                organizations.append(org)

    return organizations


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