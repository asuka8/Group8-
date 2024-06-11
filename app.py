import json
from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from config import Config
from flask_migrate import Migrate
#from model.models import User
from sqlalchemy import inspect
from flask_cors import CORS

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
#db.init_app(app)
migrate = Migrate(app, db)
#migrate.init_app(app, db)
CORS(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)

    def __repr__(self):
        return f'<User {self.username}>'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/load_attractions', methods=['GET'])
def load_attractions():
    with open('./data/attractions.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def load_markers():
    try:
        with open('./data/markers.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def save_markers(markers):
    with open('./data/markers.json', 'w', encoding='utf-8') as f:
        json.dump(markers, f, ensure_ascii=False, indent=4)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_attractions', methods=['GET'])
def get_attractions():
    attractions = load_attractions()
    return jsonify(attractions), 200

@app.route('/get_markers', methods=['GET'])
def get_markers():
    markers = load_markers()
    return jsonify(markers)

@app.route('/add_marker', methods=['POST'])
def add_marker():
    data = request.get_json()
    lat = data.get('lat')
    lng = data.get('lng')
    location_name = data.get('location_name')
    description = data.get('description', '')
    
    if lat is not None and lng is not None and location_name:
        marker = {'lat': lat, 'lng': lng, 'location_name': location_name, 'description': description, 'likes': 0, 'dislikes': 0}
        user_markers = load_markers()
        user_markers.append(marker)
        save_markers(user_markers)
        return jsonify({'message': 'Marker added successfully!'}), 200
    else:
        return jsonify({'error': 'Invalid data'}), 400

@app.route('/update_marker', methods=['POST'])
def update_marker():
    data = request.get_json()
    lat = data.get('lat')
    lng = data.get('lng')
    action = data.get('action')
    description = data.get('description', '')

    user_markers = load_markers()
    attraction_found = False

    for marker in user_markers:
        if marker['lat'] == lat and marker['lng'] == lng:
            if action == 'like':
                marker['likes'] = 1
                marker['dislikes'] = 0
            elif action == 'dislike':
                marker['likes'] = 0
                marker['dislikes'] = 1
            if description:
                marker['description'] = description
            save_markers(user_markers)
            return jsonify({'message': 'Marker updated successfully!', 'likes': marker['likes'], 'dislikes': marker['dislikes']}), 200

    if not attraction_found:
        attractions = load_attractions()
        for attraction in attractions:
            if attraction['lat'] == lat and attraction['lng'] == lng:
                new_marker = {
                    'lat': lat,
                    'lng': lng,
                    'location_name': attraction['name'],
                    'description': description,
                    'likes': 1 if action == 'like' else 0,
                    'dislikes': 1 if action == 'dislike' else 0
                }
                user_markers.append(new_marker)
                save_markers(user_markers)
                return jsonify({'message': 'Marker updated successfully!', 'likes': new_marker['likes'], 'dislikes': new_marker['dislikes']}), 200

    return jsonify({'error': 'Marker not found'}), 404

@app.route('/tables')
def tables():
    inspector = inspect(db.engine)
    tables = inspector.get_table_names()
    return jsonify(tables)

'''@app.route('/add_user', methods=['POST'])
def add_user():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if username is None or password is None:
        return jsonify({'error': 'Invalid data'}), 400

    if User.query.filter_by(username=username).first() is not None:
        return jsonify({'error': 'User already exists'}), 400

    new_user = User(username=username, password=password)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'User added successfully!'}), 201'''

@app.route('/add_user_page')
def add_user_page():
    return render_template('add_user.html')

@app.route('/add_user', methods=['POST'])
def add_user():
    username = request.form['username']
    password = request.form['password']

    if username is None or password is None:
        return jsonify({'error': 'Invalid data'}), 400

    if User.query.filter_by(username=username).first() is not None:
        return jsonify({'error': 'User already exists'}), 400

    new_user = User(username=username, password=password)
    try:
        db.session.add(new_user)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

    return redirect(url_for('get_users'))


@app.route('/get_users', methods=['GET'])
def get_users():
    users = User.query.all()
    users_list = [{'id': user.id, 'username': user.username} for user in users]
    return jsonify(users_list), 200

@app.route('/get_user/<int:id>', methods=['GET'])
def get_user(id):
    user = User.query.get(id)
    if user is None:
        return jsonify({'error': 'User not found'}), 404
    return jsonify({'id': user.id, 'username': user.username}), 200


if __name__ == '__main__':
    app.run(debug=True)
