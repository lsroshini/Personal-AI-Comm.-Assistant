from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import TfidfVectorizer
import pandas as pd

def summarize_emails(email_contents):
    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(email_contents)
    
    svd_model = TruncatedSVD(n_components=2, random_state=42)
    svd_model.fit(X)

    summarized = []
    for i in range(X.shape[0]):
        summary = " ".join([vectorizer.get_feature_names_out()[index] for index in svd_model.components_[i].argsort()[-5:][::-1]])
        summarized.append(summary)
    
    return summarized