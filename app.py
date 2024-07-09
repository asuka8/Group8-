import json
from flask import Flask, request, jsonify, render_template, redirect, url_for, abort
from flask_sqlalchemy import SQLAlchemy
from config import Config
from flask_migrate import Migrate
#from model.models import User
from sqlalchemy import inspect
from flask_cors import CORS
from datetime import date
from sqlalchemy.orm import relationship

app = Flask(__name__, template_folder='Front/html')
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
    guide = relationship('Guide', backref='user')
    userprofile = relationship('UserProfile', backref='user', uselist=False, cascade = "delete")
    like_dislike = relationship('Like_Dislike', backref='user', cascade = "delete")

    def __repr__(self):
        return f'<User {self.username}>'
    
class UserProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    bio = db.Column(db.String(1024), default='')

    def __repr__(self):
        return f"<UserProfile('{self.user_id}', '{self.bio}')>"
    
class Guide(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    content = db.Column(db.String(1024), default='')
    created_at = db.Column(db.Date, default=date.today)
    updated_at = db.Column(db.Date, default=date.today, onupdate=date.today)
    like_dislike = relationship('Like_Dislike', backref='guide', cascade = "delete")

    def __repr__(self):
        return f"<Guide('{self.user_id}', '{self.content}')>"
   
class Like_Dislike(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    guide_id = db.Column(db.Integer, db.ForeignKey('guide.id'), nullable=False)
    status = db.Column(db.Integer, nullable=False, default = 0)

    def __repr__(self):
        return f"<LikeDislike('{self.user_id}', '{self.guide_id}', '{self.status}')>"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/home')
def home():
    return render_template('home.html')

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

@app.route('/delete_user/<int:user_id>', methods=['GET', 'POST'])
def delete_user(user_id):
    user = User.query.get(user_id)
    if user is None:
        return jsonify({'error':'User not found'}), 404
    if request.method == 'POST':
        try:
            db.session.delete(user)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500
        return redirect(url_for('get_users'))
    return render_template('delete_user.html', user=user)

@app.route('/update_user/<int:user_id>', methods=['GET', 'POST'])
def update_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return abort(404, description="User not found")

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if not username and not password:
            return abort(400, description="At least one of username or password must be provided")

        if username:
            user.username = username

        if password:
            user.password = password

        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500

        return redirect(url_for('get_user', id=user_id))

    return render_template('update_user.html', user=user)

@app.route('/add_guide/<int:user_id>', methods=['GET', 'POST'])
def add_guide(user_id):
    user = User.query.get(user_id)
    if not user:
        return abort(404, description="User not found")
    if request.method == 'POST':
        content = request.form.get('content')
        if content is None:
            return abort(400, description="content is required")
        new_guide = Guide(user_id=user_id, content=content)
        try:
            db.session.add(new_guide)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500
        return redirect(url_for('get_guide', user_id=user_id))  # ここを修正
    return render_template('add_guide.html', user_id=user_id)    

@app.route('/get_guide/<int:user_id>', methods=['GET'])
def get_guide(user_id):
    #guide = Guide.query.get(user_id)    #ガイドのidになってしまっている
    guides = Guide.query.filter_by(user_id=user_id).all()
    if guides is None:
        return jsonify({'error': 'No guides found for this user'}), 404
    return jsonify([{'id': guide.id, 'user_id': guide.user_id, 'content': guide.content} for guide in guides]), 200


@app.route('/get_guide/<int:user_id>/delete_guide/<int:guide_id>', methods=['GET', 'POST'])
def delete_guide(user_id, guide_id):
    guide = Guide.query.filter_by(id=guide_id, user_id=user_id).first()
    if guide is None:
        return jsonify({'error': 'Guide not found'}), 404
    if request.method == 'POST':
        try:
            db.session.delete(guide)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500

        return redirect(url_for('get_guide', user_id=user_id)) 
    return render_template('delete_guide.html', guide=guide)

@app.route('/update_guide/<int:user_id>/<int:guide_id>', methods=['GET', 'POST'])
def update_guide(user_id, guide_id):
    user = User.query.get(user_id)
    if not user:
        return abort(404, description="User not found")
    
    guide = Guide.query.filter_by(id=guide_id, user_id=user_id).first()
    if not guide:
        return abort(404, description="Guide not found")
    
    if request.method == 'POST':
        content = request.form.get('content')
        if content is None:
            return abort(400, description="Content is required")
        guide.content = content
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500
        return redirect(url_for('get_guide', user_id=user_id))

    return render_template('update_guide.html', user_id=user_id, guide_id=guide_id, content=guide.content)


@app.route('/add_userprofile/<int:user_id>', methods = ['GET', 'POST'])
def add_userprofile(user_id):
    user = User.query.get(user_id)
    if not user:
        return abort(404, description="User not found")
    
    existing_userprofile = UserProfile.query.filter_by(user_id=user_id).first()
    if existing_userprofile:
        return redirect(url_for('update_userprofile', user_id=user_id)) #既存ならupdate_profileに移る
    
    if request.method == 'POST':
        bio = request.form.get('bio')
        if bio is None:
            return abort(400, description="bio is required")
        new_userprofile = UserProfile(user_id=user_id, bio=bio)
        try:
            db.session.add(new_userprofile)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return jsonify({'error':str(e)}), 500
        return redirect(url_for('get_userprofile', user_id=user_id))
    return render_template('add_userprofile.html', user_id=user_id)

@app.route('/get_userprofile/<int:user_id>', methods = ['GET'])
def get_userprofile(user_id):
    userprofiles = UserProfile.query.filter_by(user_id=user_id).all()
    if userprofiles is None:
        return jsonify({'error': 'No userprofiles found for this user'}), 404
    return jsonify([{'id':userprofile.id, 'user_id':userprofile.user_id, 'bio':userprofile.bio} for userprofile in userprofiles]), 200


@app.route('/delete_userprofile/<int:user_id>', methods=['GET', 'POST'])
def delete_userprofile(user_id):
    userprofile = UserProfile.query.get(user_id)
    if userprofile is None:
        return jsonify({'error':'UserProfile not found'}), 404
    if request.method == 'POST':
        try:
            db.session.delete(userprofile)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500
        return redirect(url_for('get_userprofile', user_id=user_id))
    return render_template('delete_userprofile.html', user=userprofile)

@app.route('/update_userprofile/<int:user_id>', methods=['GET', 'POST'])
def update_userprofile(user_id):
    user = User.query.get(user_id)
    if not user:
        return abort(404, description="User not found")
    
    userprofile = UserProfile.query.filter_by(user_id=user_id).first()
    if not userprofile:
        return abort(404, description="User profile not found.")
    
    if request.method == 'POST':
        bio = request.form.get('bio')
        if bio is None:
            return abort(400, description="bio is required")
        userprofile.bio = bio
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500
        return redirect(url_for('get_userprofile', user_id=user_id))

    return render_template('update_userprofile.html', user_id=user_id, bio=userprofile.bio)


if __name__ == '__main__':
    with app.app_context():
        inspector = inspect(db.engine)
        print(inspector.get_table_names())
    app.run(debug=True)
