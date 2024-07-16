import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
import json
import joblib

def load_data(json_path):
    with open(json_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    df = pd.DataFrame(data)
    return df

def preprocess_data(df):
    X = df['text']
    y = df['label']
    vectorizer = TfidfVectorizer()
    X_tfidf = vectorizer.fit_transform(X)
    return X_tfidf, y, vectorizer

def save_vectorizer(vectorizer, path='vectorizer.pkl'):
    joblib.dump(vectorizer, path)
    print('Vectorizer saved to', path)

def load_vectorizer(path='vectorizer.pkl'):
    return joblib.load(path)
