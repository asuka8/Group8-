from app import app, db

from app import app, db

with app.app_context():
    with db.get_engine().connect() as connection:
        result = connection.execute("SELECT name FROM sqlite_master WHERE type='table';")
        for row in result:
            print(row[0])
