import click
from flask import current_app
from app import db, User

@click.command("create_user")
@click.argument('username')
@click.argument('password')
def create_user(username, password):
    with current_app.app_context():
        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        print(f"User {username} created.")