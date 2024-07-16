from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_score
import joblib

def train_model(X, y):
    clf = LogisticRegression()
    clf.fit(X, y)
    return clf

def evaluate_model(clf, X, y, cv=5):
    cv_scores = cross_val_score(clf, X, y, cv=cv)
    return cv_scores.mean()

def save_model(clf, path='spam_classifier.pkl'):
    joblib.dump(clf, path)
    print('Model saved to', path)

def load_model(path='spam_classifier.pkl'):
    return joblib.load(path)
