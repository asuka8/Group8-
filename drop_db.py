# drop_db.py
from app import app, db

with app.app_context():
    db.drop_all()
    print("Dropped all tables.")
