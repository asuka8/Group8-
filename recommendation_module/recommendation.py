import json
import math
import spacy
from sklearn.feature_extraction.text import TfidfVectorizer

def haversine(lon1, lat1, lon2, lat2):
    R = 6371
    dlon = math.radians(lon2 - lon1)
    dlat = math.radians(lat2 - lat1)
    a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

nlp = spacy.load('ja_core_news_sm')
# python -m spacy download ja_core_news_sm

# INTEREST_CATEGORIES = ['history', 'nature', 'museum', 'temple', 'architecture', 'beautiful']
INTEREST_CATEGORIES = ['歴史', '自然', '博物館', '寺院', '建築', '美しい']

def preprocess_text(text):
    doc = nlp(text)
    tokens = [token.lemma_.lower() for token in doc if not token.is_stop and token.is_alpha]
    return ' '.join(tokens)

def extract_keywords(texts):
    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(texts)
    keywords = vectorizer.get_feature_names_out()
    return X, keywords

def classify_text(text, categories):
    doc = nlp(text)
    category_scores = {category: 0 for category in categories}
    for token in doc:
        if token.lemma_ in categories:
            category_scores[token.lemma_] += 1
    return category_scores

def calculate_interest_weights(user_profile, spots):
    interests = {category: 0 for category in INTEREST_CATEGORIES}
    for spot in spots:
        spot_text = preprocess_text(spot['description'])
        spot_scores = classify_text(spot_text, INTEREST_CATEGORIES)
        for category, score in spot_scores.items():
            if category in user_profile['interests']:
                interests[category] += score
    return interests

def load_scenic_spots(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        return json.load(f)

def filter_by_distance(spots, user_location, max_distance=5):
    filtered_spots = []
    for spot in spots:
        distance = haversine(user_location['lng'], user_location['lat'], spot['lng'], spot['lat'])
        if distance <= max_distance:
            spot['distance'] = distance
            filtered_spots.append(spot)
    return filtered_spots

def adjust_interests_based_on_feedback(user_profile, spots):
    for spot in spots:
        if spot['name'] in user_profile['like_dislike']:
            like = user_profile['like_dislike'][spot['name']]
            spot_text = preprocess_text(spot['description'])
            spot_scores = classify_text(spot_text, INTEREST_CATEGORIES)
            for category, score in spot_scores.items():
                if like:
                    user_profile['interests'][category] += score
                else:
                    user_profile['interests'][category] -= score

def score_spots(spots, user_profile):
    for spot in spots:
        score = 0
        spot_text = preprocess_text(spot['description'])
        spot_scores = classify_text(spot_text, INTEREST_CATEGORIES)
        for category, weight in spot_scores.items():
            if category in user_profile['interests']:
                score += weight * user_profile['interests'][category]
        spot['score'] = score - spot['distance']
    return sorted(spots, key=lambda x: x['score'], reverse=True)

def recommend_spots(user_location, user_profile, spots_filename, top_n=10):
    spots = load_scenic_spots(spots_filename)
    filtered_spots = filter_by_distance(spots, user_location)
    adjust_interests_based_on_feedback(user_profile, filtered_spots)
    scored_spots = score_spots(filtered_spots, user_profile)
    return scored_spots[:top_n]
