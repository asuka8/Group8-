from recommendation import recommend_spots
from user_profile_feature_extract import extract_interests, INTEREST_CATEGORIES
import os

user_location = {'lng': 135.7681, 'lat': 35.0116}  #ここをかえる

user_description = "歴史と寺院に特に興味があります。建築や博物館も好きで、自然や美しい風景を楽しむこともあります。" #ここを変える
user_interests = extract_interests(user_description, INTEREST_CATEGORIES)
print(user_interests) #プロフィールのみの結果

user_profile = {
    'interests': user_interests,
    'like_dislike': {   #ここを変える
        '清水寺': True,
        '京都御所': False,
        '嵐山': True,
        '先斗町': False
    }
}

script_dir = os.path.dirname(os.path.abspath(__file__))
filename = os.path.join(script_dir, 'attractions.json')

recommended_spots = recommend_spots(user_location, user_profile, filename)

print(user_interests) #プロフィール+スポットの好き嫌いの情報の結果

for spot in recommended_spots:
    print(f"{spot['name']}: {spot['score']}, 距離: {spot['distance']}km")
