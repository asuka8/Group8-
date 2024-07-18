import json
from datetime import date
from flask import Flask
from config import Config
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app import db, app, Guide 

# JSONファイルのパス
json_file_path = 'data/attractions.json'

# JSONファイルを読み込む
with open(json_file_path, 'r', encoding='utf-8') as f:
    attractions = json.load(f)

# データをGuideモデルに変換して追加
with app.app_context():
    for attraction in attractions:
        guide = Guide(
            user_id=1,
            latitude=attraction['lat'],
            longitude=attraction['lng'],
            title=attraction['name'],
            content=attraction['description'],
            created_at=date.today(),
            updated_at=date.today()
        )
        db.session.add(guide)

    # データベースにコミット
    db.session.commit()

    # セッションを閉じる
    db.session.close()

print("ダミーデータの挿入が完了しました。")
