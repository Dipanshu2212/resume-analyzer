import streamlit as st
import sys
import os

@st.cache_resource
def load_ner_model():
    import spacy
    return spacy.load("en_core_web_lg")

# ── Path setup ─────────────────────────────────────────────────────────────────
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

try:
    from analyzer.parser import parse_resume
    from analyzer.ner import analyze_resume
except Exception as e:
    st.error(f"Failed to load modules: {e}")
    st.stop()

st.set_page_config(page_title="Resume Analyzer", page_icon="📄", layout="wide")

st.title("📄 Resume Analyzer")
st.markdown("Upload your resume and we'll extract your skills, contact info, and more.")

st.divider()

# ── File Upload ────────────────────────────────────────────────────────────────
uploaded_file = st.file_uploader(
    "Upload your resume",
    type=["pdf", "docx"],
    help="Supported formats: PDF, DOCX"
)

if uploaded_file is not None:

    with st.spinner("Parsing resume..."):
        try:
            resume_text = parse_resume(uploaded_file)
        except ValueError as e:
            st.error(str(e))
            st.stop()

    if not resume_text.strip():
        st.error("Could not extract text from your resume. Make sure it's not a scanned image.")
        st.stop()

    with st.spinner("Analyzing resume with NLP..."):
        result = analyze_resume(resume_text)

    # ── Save to session state for other pages ──────────────────────────────────
    st.session_state["resume_text"]   = resume_text
    st.session_state["resume_result"] = result

    st.success("Resume analyzed successfully!")
    st.divider()

    # ── Contact Info ───────────────────────────────────────────────────────────
    st.subheader("👤 Contact Information")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Name",  result["name"]  or "Not detected")
    with col2:
        st.metric("Email", result["email"] or "Not detected")
    with col3:
        st.metric("Phone", result["phone"] or "Not detected")

    st.divider()

    # ── Skills ─────────────────────────────────────────────────────────────────
    st.subheader("🛠️ Skills Detected")

    if result["skills"]:
        st.success(f"Found **{len(result['skills'])}** skills in your resume")

        # Display skills as colored tags
        skills_html = " ".join([
            f'<span style="background:#e8f4fd; color:#1f77b4; padding:4px 10px; '
            f'border-radius:20px; margin:3px; display:inline-block; '
            f'font-size:0.85rem; font-weight:600;">{skill}</span>'
            for skill in result["skills"]
        ])
        st.markdown(skills_html, unsafe_allow_html=True)
    else:
        st.warning("No skills detected. Make sure your resume has a Skills section.")

    st.divider()

    # ── Organizations ──────────────────────────────────────────────────────────
    st.subheader("🏢 Organizations Detected")

    if result["organizations"]:
        for org in result["organizations"]:
            st.markdown(f"- {org}")
    else:
        st.info("No organizations detected.")

    st.divider()

    # ── Sections ───────────────────────────────────────────────────────────────
    st.subheader("📋 Resume Sections")

    cols = st.columns(len(result["sections"]))
    for col, (section, present) in zip(cols, result["sections"].items()):
        with col:
            if present:
                st.success(f"✓ {section.capitalize()}")
            else:
                st.error(f"✗ {section.capitalize()}")

    st.divider()

    # ── Raw Text Preview ───────────────────────────────────────────────────────
    with st.expander("📃 View Extracted Raw Text"):
        st.text_area("Raw Text", resume_text, height=300)

    st.info("👈 Go to **Job Matcher** in the sidebar to match your resume with jobs.")

else:
    st.info("Please upload a PDF or DOCX resume to get started.")