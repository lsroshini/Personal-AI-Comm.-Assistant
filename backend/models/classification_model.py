import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import make_pipeline
import joblib

def train_model():
    data = pd.read_csv('data/email_priority_dataset.csv')
    X = data['Body']
    y = data['Priority']
    print(X)

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = make_pipeline(TfidfVectorizer(), RandomForestClassifier())
    model.fit(X_train, y_train)

    joblib.dump(model, 'models/email_classifier.joblib')
    print("Model trained and saved.")

def load_model():
    return joblib.load('models/email_classifier.joblib')