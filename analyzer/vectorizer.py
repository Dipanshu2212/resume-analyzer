def get_bert_model():
    from sentence_transformers import SentenceTransformer
    return SentenceTransformer('all-MiniLM-L6-v2')


def get_tfidf_vectors(text1: str, text2: str):
    from sklearn.feature_extraction.text import TfidfVectorizer

    vectorizer = TfidfVectorizer(
        stop_words='english',
        ngram_range=(1, 2),
        min_df=1
    )

    matrix  = vectorizer.fit_transform([text1, text2])
    vector1 = matrix[0]
    vector2 = matrix[1]

    return vector1, vector2


def get_bert_embedding(text: str):
    import numpy as np
    truncated = " ".join(text.split()[:512])
    model     = get_bert_model()
    embedding = model.encode(truncated, convert_to_numpy=True)
    return embedding


def get_tfidf_similarity(text1: str, text2: str) -> float:
    from sklearn.metrics.pairwise import cosine_similarity

    vec1, vec2 = get_tfidf_vectors(text1, text2)
    score      = cosine_similarity(vec1, vec2)[0][0]

    return round(float(score), 4)


def get_bert_similarity(text1: str, text2: str) -> float:
    from sklearn.metrics.pairwise import cosine_similarity

    emb1  = get_bert_embedding(text1).reshape(1, -1)
    emb2  = get_bert_embedding(text2).reshape(1, -1)
    score = cosine_similarity(emb1, emb2)[0][0]

    return round(float(score), 4)


def get_combined_score(text1: str, text2: str) -> dict:
    tfidf_score = get_tfidf_similarity(text1, text2)
    bert_score  = get_bert_similarity(text1, text2)
    combined    = round((0.4 * tfidf_score) + (0.6 * bert_score), 4)

    return {
        "tfidf_score"   : tfidf_score,
        "bert_score"    : bert_score,
        "combined_score": combined
    }


# ── Local test ─────────────────────────────────────────────────────────────────
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