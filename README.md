# 📄 Resume Analyzer & Job Matcher

An AI-powered resume analysis tool that extracts skills, matches job descriptions, scores resumes against ATS systems, and provides actionable improvement suggestions — built with spaCy, BERT, TF-IDF, and Streamlit.

---

## 🚀 Live Demo

> [Add your Streamlit Cloud URL here after deployment]

---

## ✨ Features

- **Resume Parsing** — Upload PDF or DOCX resumes and extract raw text automatically
- **NLP Analysis** — Extract name, email, phone, organizations, and skills using spaCy NER
- **Job Matching** — Match your resume against job descriptions using BERT embeddings + TF-IDF cosine similarity
- **ATS Scoring** — Get an ATS score out of 100 broken down by keywords, sections, format, and skills
- **Improvement Suggestions** — Get actionable tips including missing keywords, skill gaps, and formatting fixes

---

## 🧠 Tech Stack

| Component | Technology |
|---|---|
| Language | Python 3.11 |
| Frontend | Streamlit |
| NLP & NER | spaCy `en_core_web_md` |
| Semantic Similarity | BERT (`all-MiniLM-L6-v2`) via sentence-transformers |
| Keyword Matching | TF-IDF (scikit-learn) |
| PDF Parsing | pdfplumber |
| DOCX Parsing | python-docx |
| Similarity Metric | Cosine Similarity |

---

## 📁 Project Structure

```
resume_analyzer/
│
├── app.py                          # Streamlit homepage
│
├── pages/
│   ├── 1_Resume_Analyzer.py        # Upload & analyze resume
│   ├── 2_Job_Matcher.py            # Match resume with job descriptions
│   ├── 3_ATS_Scorer.py             # ATS score breakdown
│   └── 4_Improvements.py          # Suggestions & gap analysis
│
├── analyzer/
│   ├── __init__.py
│   ├── parser.py                   # PDF/DOCX text extraction
│   ├── ner.py                      # spaCy NER — extract entities & skills
│   ├── vectorizer.py               # TF-IDF + BERT embeddings
│   ├── matcher.py                  # Cosine similarity + job ranking
│   ├── scorer.py                   # ATS scoring logic
│   └── suggester.py                # Gap analysis + suggestions
│
├── data/
│   ├── job_descriptions.json       # Sample job descriptions
│   └── skills_list.json            # Master list of known skills
│
├── requirements.txt
└── README.md
```

---

## ⚙️ Installation & Setup

### 1. Clone the repository

```bash
git clone https://github.com/Dipanshu2212/resume-analyzer.git
cd resume-analyzer
```

### 2. Create a virtual environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Download spaCy model

```bash
python -m spacy download en_core_web_md
```

### 5. Run the app

```bash
streamlit run app.py
```

---

## 📖 How It Works

```
User uploads resume (PDF/DOCX)
        ↓
parser.py → extracts raw text
        ↓
ner.py → extracts skills, name, email, organizations, sections
        ↓
vectorizer.py → TF-IDF vector + BERT embedding
        ↓
        ├──→ matcher.py   → cosine similarity vs job descriptions
        ├──→ scorer.py    → ATS score breakdown (out of 100)
        └──→ suggester.py → missing skills + improvement suggestions
```

### Scoring Breakdown

| Category | Weight | What it checks |
|---|---|---|
| Keywords | 35 pts | TF-IDF overlap with job description |
| Sections | 25 pts | Presence of Experience, Education, Skills, etc. |
| Format | 20 pts | Email, phone, word count, action verbs |
| Skills | 20 pts | Skills matched against job description |

### Similarity Score

| Score | Meaning |
|---|---|
| TF-IDF (40%) | Exact keyword overlap |
| BERT (60%) | Semantic meaning similarity |
| Combined | Weighted final match percentage |

---

## 🖥️ Pages

### 1. Resume Analyzer
Upload your PDF or DOCX resume and instantly see:
- Extracted contact information (name, email, phone)
- Detected skills shown as tags
- Organizations identified
- Resume sections present/missing

### 2. Job Matcher
Two modes:
- **Database mode** — match against 8 built-in job descriptions and get ranked results
- **Custom mode** — paste any job description and get an instant match score

### 3. ATS Scorer
Get a detailed ATS score out of 100 with:
- Per-category score breakdown
- Visual progress bars
- Section-by-section analysis
- Format quality indicators

### 4. Improvements
Get actionable suggestions including:
- Missing skills highlighted in yellow
- Missing keywords highlighted in red
- Specific suggestions for sections, format, and content
- General ATS tips

---

## 📦 Dependencies

```
streamlit
pdfplumber
python-docx
spacy
scikit-learn
sentence-transformers
torch
numpy
```

---

## 🚀 Deployment on Streamlit Cloud

1. Push your code to GitHub (see below)
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub repository
4. Set main file as `app.py`
5. Deploy

---

## 🤝 Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

---

## 📄 License

[MIT](https://choosealicense.com/licenses/mit/)

---

## 👤 Author

**Dipanshu Rawat**
- LinkedIn: [linkedin.com/in/dipanshu-rawat](https://linkedin.com/in/dipanshu-rawat)
- Email: dipanshurawat2002@gmail.com
- GitHub: [@YOUR_USERNAME](https://github.com/Dipanshu2212)