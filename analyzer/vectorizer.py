from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
import numpy as np

# ── Load BERT model once at module level ──────────────────────────────────────
# all-MiniLM-L6-v2 is fast, lightweight (~90MB) and accurate enough for resumes
print("Loading BERT model... (first time may take a minute)")
bert_model = SentenceTransformer('all-MiniLM-L6-v2')
print("BERT model loaded.")


# ──────────────────────────────────────────────────────────────────────────────
# FUNCTION 1: TF-IDF Vectors
# ──────────────────────────────────────────────────────────────────────────────
def get_tfidf_vectors(text1: str, text2: str):
    """
    Convert two texts into TF-IDF vectors using a shared vocabulary.

    IMPORTANT: Both texts are fit together so they share the same
    vocabulary space — required for meaningful cosine similarity.

    Args:
        text1: Resume text
        text2: Job description text

    Returns:
        Tuple of (vector1, vector2) as sparse matrices
    """
    vectorizer = TfidfVectorizer(
        stop_words='english',       # remove common words like "the", "and"
        ngram_range=(1, 2),         # capture single words AND two-word phrases
        min_df=1                    # include all terms
    )

    # fit_transform on both together — shared vocabulary
    matrix = vectorizer.fit_transform([text1, text2])

    vector1 = matrix[0]             # resume vector
    vector2 = matrix[1]             # job description vector

    return vector1, vector2


# ──────────────────────────────────────────────────────────────────────────────
# FUNCTION 2: BERT Embedding
# ──────────────────────────────────────────────────────────────────────────────
def get_bert_embedding(text: str) -> np.ndarray:
    """
    Generate a BERT sentence embedding for a given text.

    Truncates to first 512 words to stay within BERT's token limit.
    The embedding is a 384-dimensional vector (for MiniLM model).

    Args:
        text: Any text string

    Returns:
        numpy array of shape (384,)
    """
    # Truncate to 512 words — BERT has token limit
    truncated = " ".join(text.split()[:512])

    embedding = bert_model.encode(truncated, convert_to_numpy=True)

    return embedding


# ──────────────────────────────────────────────────────────────────────────────
# FUNCTION 3: Compute TF-IDF cosine similarity
# ──────────────────────────────────────────────────────────────────────────────
def get_tfidf_similarity(text1: str, text2: str) -> float:
    """
    Compute cosine similarity between two texts using TF-IDF vectors.

    Args:
        text1: Resume text
        text2: Job description text

    Returns:
        Float between 0 and 1 (1 = identical, 0 = completely different)
    """
    vec1, vec2 = get_tfidf_vectors(text1, text2)

    # cosine_similarity returns a 2D array [[score]] — extract scalar
    score = cosine_similarity(vec1, vec2)[0][0]

    return round(float(score), 4)


# ──────────────────────────────────────────────────────────────────────────────
# FUNCTION 4: Compute BERT cosine similarity
# ──────────────────────────────────────────────────────────────────────────────
def get_bert_similarity(text1: str, text2: str) -> float:
    """
    Compute cosine similarity between two texts using BERT embeddings.
    BERT captures semantic meaning — "developer" ≈ "engineer" etc.

    Args:
        text1: Resume text
        text2: Job description text

    Returns:
        Float between 0 and 1
    """
    emb1 = get_bert_embedding(text1).reshape(1, -1)     # reshape for cosine_similarity
    emb2 = get_bert_embedding(text2).reshape(1, -1)

    score = cosine_similarity(emb1, emb2)[0][0]

    return round(float(score), 4)


# ──────────────────────────────────────────────────────────────────────────────
# FUNCTION 5: Combined score (main function used by matcher.py)
# ──────────────────────────────────────────────────────────────────────────────
def get_combined_score(text1: str, text2: str) -> dict:
    """
    Compute a weighted combination of TF-IDF and BERT similarity scores.

    Weights:
        - BERT  : 60% — semantic understanding (meaning-aware)
        - TF-IDF: 40% — keyword overlap (exact term matching)

    Args:
        text1: Resume text
        text2: Job description text

    Returns:
        Dictionary with individual and combined scores:
        {
            "tfidf_score": float,
            "bert_score": float,
            "combined_score": float
        }
    """
    tfidf_score = get_tfidf_similarity(text1, text2)
    bert_score  = get_bert_similarity(text1, text2)

    combined = round((0.4 * tfidf_score) + (0.6 * bert_score), 4)

    return {
        "tfidf_score"   : tfidf_score,
        "bert_score"    : bert_score,
        "combined_score": combined
    }


# ──────────────────────────────────────────────────────────────────────────────
# Local test — run: python -m analyzer.vectorizer
# ──────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    resume_sample = """
    Experienced Python developer with 3 years of experience in machine learning
    and data science. Proficient in TensorFlow, scikit-learn, and SQL.
    Worked at Google as a software engineer. Strong communication skills.
    """

    job_sample = """
    We are looking for a Python developer with experience in machine learning.
    The candidate should know TensorFlow, deep learning, and data analysis.
    Experience with SQL and cloud platforms is a plus.
    """

    print("Computing similarity scores...\n")
    result = get_combined_score(resume_sample, job_sample)

    print(f"TF-IDF Score   : {result['tfidf_score']}")
    print(f"BERT Score     : {result['bert_score']}")
    print(f"Combined Score : {result['combined_score']}")