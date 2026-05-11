from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity 

def calculate_similarity(resume_text, job_description):

    documents = [resume_text, job_description]
    vectorizer = TfidfVectorizer()

    vectors = vectorizer.fit_transform(documents)

    similarity = cosine_similarity(vectors)

    return similarity[0][1]*100
