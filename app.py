import json
from flask import Flask, request, jsonify, render_template, redirect, url_for, abort, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from config import Config
from flask_migrate import Migrate
#from model.models import User
from sqlalchemy import inspect
from flask_cors import CORS
from datetime import date
from sqlalchemy.orm import relationship
from sqlalchemy import event


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
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, unique=True)
    bio = db.Column(db.String(1024), default='')

    def __repr__(self):
        return f"<UserProfile('{self.user_id}', '{self.bio}')>"
    
class Guide(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    title = db.Column(db.String(1024), default='')
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

# Userと同時にUserprofileも作成
'''@event.listens_for(User, 'after_insert')
def create_user_profile(mapper, connection, target):
    try:
        new_profile = UserProfile(user_id=target.id)
        connection.execute(UserProfile.__table__.insert(), {'user_id': target.id})
    except Exception as e:
        db.session.rollback()
        raise e'''
    
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()

        if user and password==user.password:
            session['user_id'] = user.id
            flash('Login successful!', 'success')
            return redirect(url_for('user_page', user_id=user.id)) 
        else:
            flash('Invalid username or password', 'danger')
            return render_template('login.html', error='Invalid username or password')

    return render_template('login.html')


@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/user/<int:user_id>')
def user_page(user_id):
    user = User.query.get(user_id)
    userprofile = UserProfile.query.filter_by(user_id=user_id).first()
    guides = Guide.query.filter_by(user_id=user_id).all()
    if not user:
        return abort(404, description="User not found")
    if not userprofile:
        return abort(404, description="User not found")
    return render_template('home.html', user=user, userprofile=userprofile, guides=guides)

@app.route('/user/<int:user_id>/update', methods=['POST'])
def update_profile(user_id):
    user = User.query.get(user_id)
    if not user:
        return abort(404, description="User not found")
    userprofile = UserProfile.query.filter_by(user_id=user_id).first()
    if not userprofile:
        return abort(404, description="User profile not found")
    
    username = request.form['username']
    bio = request.form['bio']
    
    user.username = username
    userprofile.bio = bio
    
    db.session.commit()
    
    return redirect(url_for('user_page', user_id=user_id))

@app.route('/map/<int:user_id>', methods=['GET', 'POST'])
def map(user_id):
    user = User.query.get(user_id)
    if not user:
        return abort(404, description="User not found")
    return render_template('index.html', user=user)

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

    if description:
        from junk_classify_module import classification
        if classification.classify_message(description) == 1:
            return abort(400, description="Junk content")
    
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

    if description:
        from junk_classify_module import classification
        if classification.classify_message(description) == 1:
            return abort(400, description="Junk content")

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
    return render_template('register.html')

@app.route('/add_user', methods=['POST'])
def add_user():
    username = request.form['username']
    password = request.form['password']
    confirmPassword = request.form['confirmPassword']

    if username is None or password is None:
        return jsonify({'error': 'Invalid data'}), 400

    if User.query.filter_by(username=username).first() is not None:
        return jsonify({'error': 'User already exists'}), 400
    
    if password != confirmPassword:
        return jsonify({'error': 'Passwords do not match'}), 400

    new_user = User(username=username, password=password)
    try:
        db.session.add(new_user)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
    new_userprofile = UserProfile(user_id=new_user.id, bio='')
    try:
        db.session.add(new_userprofile)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
    return redirect(url_for('login'))    # ここを修正


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

"""@app.route('/add_guide/<int:user_id>', methods=['GET', 'POST'])
def add_guide(user_id):
    from junk_classify_module import classification
    user = User.query.get(user_id)
    if not user:
        return abort(404, description="User not found")
    if request.method == 'POST':
        content = request.form.get('content')
        if content is None:
            return abort(400, description="content is required")
        
        if classification.classify_message(content) == 1:
            return jsonify({'error': "Junk Input"}), 500

        else:
            new_guide = Guide(user_id=user_id, content=content)
            try:
                db.session.add(new_guide)
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                return jsonify({'error': str(e)}), 500
            return redirect(url_for('get_guide', user_id=new_guide.id))
    
    return render_template('add_guide.html', user_id=user_id)    """

@app.route('/add_guide/<int:user_id>', methods=['GET', 'POST'])
def add_guide(user_id):
    from junk_classify_module import classification
    user = User.query.get(user_id)

    if not user:
        return abort(404, description="User not found")
    
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')

        if content is None:
            return abort(400, description="content is required")

        if classification.classify_message(content) == 1:
            return abort(400, description="Junk content")

        else:
            new_guide = Guide(user_id=user_id, title=title, content=content)
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
    return jsonify([{'id': guide.id, 'user_id': guide.user_id, 'title': guide.title, 'content': guide.content} for guide in guides]), 200

@app.route('/get_userprofiles', methods=['GET'])
def get_userprofiles():
    userprofiles = UserProfile.query.all()
    userprofiles_list = [{'id': userprofile.id, 'userid': userprofile.user_id, 'bio': userprofile.bio} for userprofile in userprofiles]
    return jsonify(userprofiles_list), 200

if __name__ == '__main__':
    with app.app_context():
        inspector = inspect(db.engine)
        print(inspector.get_table_names())
    app.run(debug=True)
