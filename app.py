import streamlit as st

st.set_page_config(
    page_title="Resume Analyzer",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
    <style>
        .main-title {
            font-size: 3rem;
            font-weight: 800;
            color: #1f77b4;
            text-align: center;
            margin-bottom: 0.2rem;
        }
        .subtitle {
            font-size: 1.2rem;
            color: #555;
            text-align: center;
            margin-bottom: 2rem;
        }
        .feature-card {
            background: #f8f9fa;
            border-left: 4px solid #1f77b4;
            padding: 1rem 1.5rem;
            border-radius: 6px;
            margin-bottom: 1rem;
        }
        .feature-title {
            font-weight: 700;
            font-size: 1.1rem;
            color: #1f77b4;
        }
        .step-box {
            background: #e8f4fd;
            padding: 1rem;
            border-radius: 8px;
            text-align: center;
            font-weight: 600;
        }
    </style>
""", unsafe_allow_html=True)


# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown('<div class="main-title">📄 Resume Analyzer</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">AI-powered resume analysis, job matching & ATS scoring</div>', unsafe_allow_html=True)

st.divider()

# ── How it works ───────────────────────────────────────────────────────────────
st.subheader("🚀 How It Works")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown('<div class="step-box" style="color: black;">① Upload Resume<br><small>PDF or DOCX</small></div>', unsafe_allow_html=True)
with col2:
    st.markdown('<div class="step-box" style="color: black;">② Analyze Skills<br><small>NER + spaCy</small></div>', unsafe_allow_html=True)
with col3:
    st.markdown('<div class="step-box" style="color: black;">③ Match Jobs<br><small>BERT + TF-IDF</small></div>', unsafe_allow_html=True)
with col4:
    st.markdown('<div class="step-box" style="color: black;">④ Get Score<br><small>ATS Scoring</small></div>', unsafe_allow_html=True)

st.divider()

# ── Features ───────────────────────────────────────────────────────────────────
st.subheader("✨ Features")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    <div class="feature-card" style="color: black;">
        <div class="feature-title">📊 Resume Analyzer</div>
        Extract your skills, contact info, organizations, and sections
        automatically using NLP and Named Entity Recognition.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="feature-card" style="color: black;">
        <div class="feature-title">🎯 ATS Scorer</div>
        Get an ATS score out of 100 broken down by keywords,
        sections, format quality, and skills coverage.
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="feature-card" style="color: black;">
        <div class="feature-title">💼 Job Matcher</div>
        Match your resume against job descr style="color: black;"iptions using
        BERT embeddings and TF-IDF cosine similarity.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="feature-card" style="color: black;">
        <div class="feature-title">💡 Improvement Suggestions</div>
        Get actionable suggestions to improve your resume —
        missing keywords, skills gaps, and formatting fixes.
    </div>
    """, unsafe_allow_html=True)

st.divider()

# ── Get started CTA ────────────────────────────────────────────────────────────
st.subheader("👈 Get Started")
st.info("Upload your resume on the **Resume Analyzer** page from the sidebar to begin.")

# ── Tech stack ─────────────────────────────────────────────────────────────────
with st.expander("🛠️ Tech Stack"):
    st.markdown("""
    | Component | Technology |
    |---|---|
    | NLP & NER | spaCy `en_core_web_sm` |
    | Semantic Similarity | BERT (`all-MiniLM-L6-v2`) |
    | Keyword Matching | TF-IDF (scikit-learn) |
    | PDF Parsing | pdfplumber |
    | DOCX Parsing | python-docx |
    | Frontend | Streamlit |
    """)