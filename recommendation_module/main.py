from recommendation import recommend_spots
from user_profile_feature_extract import extract_interests, INTEREST_CATEGORIES

user_location = {'lng': 135.7681, 'lat': 35.0116}

user_description = "歴史と寺院に特に興味があります。建築や博物館も好きで、自然や美しい風景を楽しむこともあります。"
user_interests = extract_interests(user_description, INTEREST_CATEGORIES)
print(user_interests)

user_profile = {
    'interests': user_interests,
    'like_dislike': {
        '清水寺': True,
        '京都御所': False,
        '嵐山': True,
        '先斗町': False
    }
}

recommended_spots = recommend_spots(user_location, user_profile, './attractions.json')

print(user_interests)

for spot in recommended_spots:
    print(f"{spot['name']}: {spot['score']}, 距離: {spot['distance']}km")
