# drop_alembic_version.py
from app import db
from app import app
from sqlalchemy import text

with app.app_context():
    with db.engine.connect() as connection:
        connection.execute(text('DROP TABLE IF EXISTS alembic_version'))
        print("Dropped alembic_version table.")
