import json
from flask import Flask, request, jsonify, render_template, redirect, url_for, abort, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from config import Config
from flask_migrate import Migrate
#from model.models import User
from sqlalchemy import inspect, UniqueConstraint
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

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'password': self.password
        }

    def __repr__(self):
        return f'<User {self.username}>'
    
class UserProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, unique=True)
    bio = db.Column(db.String(1024), default='')
    language = db.Column(db.String(2), nullable=False, default='ja')  # 言語情報を追加

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'bio': self.bio,
            'language': self.language,
        }

    def __repr__(self):
        return f"<UserProfile('{self.user_id}', '{self.bio}')>"
    
class Guide(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    title = db.Column(db.String(1024), default='')
    content = db.Column(db.String(1024), default='')
    created_at = db.Column(db.Date, default=date.today)
    updated_at = db.Column(db.Date, default=date.today, onupdate=date.today)
    like_dislike = relationship('Like_Dislike', backref='guide', cascade = "delete")

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'title': self.title,
            'content': self.content
        }

    def __repr__(self):
        return f"<Guide('{self.user_id}', '{self.content}')>"
   
class Like_Dislike(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    guide_id = db.Column(db.Integer, db.ForeignKey('guide.id'), nullable=False)
    status = db.Column(db.Integer, nullable=False, default = 0)
    __table_args__ = (UniqueConstraint('user_id', 'guide_id', name='uix_user_guide'),)
#statusを1, -1, 0でLike, Dislike, どちらでもないとして扱う
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'guide_id': self.guide_id,
            'status': self.status
        }

    def __repr__(self):
        return f"<LikeDislike('{self.user_id}', '{self.guide_id}', '{self.status}')>"
    
    
'''@app.route('/')
def index():
    return render_template('index.html')'''

@app.route('/', methods=['GET', 'POST'])
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


'''@app.route('/home')
def home():
    return render_template('home.html')'''

@app.route('/user/<int:user_id>')
def user_page(user_id):
    user = User.query.get(user_id)
    userprofile = UserProfile.query.filter_by(user_id=user_id).first()

    if not user:
        return abort(404, description="User not found")
    if not userprofile:
        return abort(404, description="User not found")
    
    guides = Guide.query.filter_by(user_id=user_id).all()
    liked_dislikes = Like_Dislike.query.filter_by(user_id=user_id, status=1).all()
    liked_guide_ids = [ld.guide_id for ld in liked_dislikes]
    liked_guides = Guide.query.filter(Guide.id.in_(liked_guide_ids)).all()

    return render_template('home.html', user=user, userprofile=userprofile, guides=guides, liked_guides=liked_guides)

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
    language = request.form['language']
    
    user.username = username
    userprofile.bio = bio
    userprofile.language = language
    
    db.session.commit()
    
    return redirect(url_for('user_page', user_id=user_id))

@app.route('/map/<int:user_id>', methods=['GET', 'POST'])
def map(user_id):
    user = User.query.get(user_id)
    like_dislike = Like_Dislike.query.filter_by(user_id=user_id).all()
    if not user:
        return abort(404, description="User not found")
    like_dislike_dict = [ld.to_dict() for ld in like_dislike]  # Convert objects to dicts
    return render_template('index.html', user=user, like_dislike=like_dislike_dict)

@app.route('/map_ver2/<int:user_id>', methods=['GET', 'POST'])
def map_ver2(user_id):
    user = User.query.get(user_id)
    userprofile = UserProfile.query.filter_by(user_id=user_id).first()
    guides = Guide.query.all()
    like_dislike = Like_Dislike.query.filter_by(user_id=user_id).all()
    if not user:
        return abort(404, description="User not found")
    user_dict = user.to_dict()  # Convert object to dict
    userprofile_dict = userprofile.to_dict()  # Convert object to dict
    guides_dict = [guide.to_dict() for guide in guides]  # Convert objects to dicts
    like_dislike_dict = [ld.to_dict() for ld in like_dislike]  # Convert objects to dicts
    return render_template('index_ver3.html', user=user, userprofile=userprofile_dict, user_json=user_dict, guides=guides_dict, like_dislike=like_dislike_dict)

@app.route('/get_all_data', methods=['GET'])
def get_all_data():
    guides = Guide.query.all()
    like_dislikes = Like_Dislike.query.all()
    guides_dict = [guide.to_dict() for guide in guides]  # Convert objects to dicts
    like_dislike_dict = [ld.to_dict() for ld in like_dislikes]  # Convert objects to dicts
    return jsonify({'guides': guides_dict, 'like_dislikes': like_dislike_dict})

@app.route('/delete_null_coordinates_guides', methods=['DELETE'])
def delete_null_coordinates_guides():
    guides_to_delete = Guide.query.filter((Guide.latitude == None) | (Guide.longitude == None)).all()
    
    if not guides_to_delete:
        return jsonify({"message": "No guides with null coordinates found"}), 404

    for guide in guides_to_delete:
        db.session.delete(guide)
    
    db.session.commit()

    return jsonify({"message": f"{len(guides_to_delete)} guides deleted successfully"}), 200


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

@app.route('/add_marker/<int:user_id>', methods=['POST'])
def add_marker(user_id):
    user = User.query.get(user_id)
    data = request.get_json()
    lat = data.get('lat')
    lng = data.get('lng')
    location_name = data.get('location_name')
    description = data.get('description', '')

    '''if description:
        from junk_classify_module import classification
        if classification.classify_message(description) == 1:
            return abort(400, description="Junk content")'''
    
    if lat is not None and lng is not None and location_name and user:
        #marker = {'lat': lat, 'lng': lng, 'location_name': location_name, 'description': description, 'likes': 0, 'dislikes': 0}
        #user_markers = load_markers()
        #user_markers.append(marker)
        #save_markers(user_markers)
        new_guide = Guide(user_id=user_id, latitude=lat, longitude=lng, title=location_name, content=description)
        try:
            db.session.add(new_guide)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500
        return jsonify({'message': 'Marker added successfully!'}), 200
    else:
        return jsonify({'error': 'Invalid data'}), 400

@app.route('/update_marker/<int:user_id>', methods=['POST'])   #使っていない
def update_marker(user_id):
    user = User.query.get(user_id)
    data = request.get_json()
    lat = data.get('lat')
    lng = data.get('lng')
    action = data.get('action')
    description = data.get('description', '')  #マップから文章変更はできないので、いらないかも

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
            if user:
                guide = Guide.query.filter_by(latitude=lat, longitude=lng).first()
                existing_like_dislike = Like_Dislike.query.filter_by(user_id=user_id, guide_id=guide.id).first()
                if action == 'like':
                    status_value = 1
                elif action == 'dislike':
                    status_value = -1
                if existing_like_dislike:
                    existing_like_dislike.status = status_value
                else:
                    new_like_dislike = Like_Dislike(user_id=user_id, guide_id=guide.id, status=status_value)
                    db.session.add(new_like_dislike) 
                try:
                    db.session.commit()
                except Exception as e:
                    db.session.rollback()
                    return jsonify({'error': str(e)}), 500
                return jsonify({'message': 'Marker updated successfully!', 'likes': marker['likes'], 'dislikes': marker['dislikes']}), 200

    if not attraction_found:
        attractions = load_attractions()
        for attraction in attractions:
            if attraction['lat'] == lat and attraction['lng'] == lng:
                new_marker = {
                    'lat': lat,
                    'lng': lng,
                    'location_name': attraction['name'],
                    'description': attraction['description'],
                    'likes': 1 if action == 'like' else 0,
                    'dislikes': 1 if action == 'dislike' else 0
                }
                user_markers.append(new_marker)
                save_markers(user_markers)
                return jsonify({'message': 'Marker updated successfully!', 'likes': new_marker['likes'], 'dislikes': new_marker['dislikes']}), 200

    return jsonify({'error': 'Marker not found'}), 404

@app.route('/update_marker_ver2/<int:user_id>', methods=['POST'])
def update_marker_ver2(user_id):
    app.logger.debug('Received request for user_id: %s', user_id)
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    data = request.get_json()
    app.logger.debug('Received data: %s', data)
    if not data:
        return jsonify({'error': 'No input data provided'}), 400

    lat = data.get('lat')
    lng = data.get('lng')
    action = data.get('action')
    description = data.get('description', '')  # Unused, can be removed if not needed

    # Validate required fields
    if lat is None or lng is None or action is None:
        app.logger.debug('Missing data fields: lat=%s, lng=%s, action=%s', lat, lng, action)
        return jsonify({'error': 'Missing data fields'}), 400

    # Optional: Junk content classification
    '''if description:
        from junk_classify_module import classification
        if classification.classify_message(description) == 1:
            return abort(400, description="Junk content")'''

    guide = Guide.query.filter_by(latitude=lat, longitude=lng).first()
    if not guide:
        return jsonify({'error': 'Guide not found'}), 404

    existing_like_dislike = Like_Dislike.query.filter_by(user_id=user_id, guide_id=guide.id).first()
    if action == 'like':
        status_value = 1
    elif action == 'dislike':
        status_value = -1
    else:
        app.logger.debug('Invalid action: %s', action)
        return jsonify({'error': 'Invalid action'}), 400

    if existing_like_dislike:
        existing_like_dislike.status = status_value
    else:
        new_like_dislike = Like_Dislike(user_id=user_id, guide_id=guide.id, status=status_value)
        db.session.add(new_like_dislike)

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        app.logger.error('Database commit error: %s', str(e))
        return jsonify({'error': str(e)}), 500

    app.logger.debug('Marker updated successfully')
    return jsonify({'message': 'Marker updated successfully!'}), 200


@app.route('/tables')
def tables():
    inspector = inspect(db.engine)
    tables = inspector.get_table_names()
    return jsonify(tables)

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

@app.route('/add_guide/<int:user_id>', methods=['GET', 'POST'])
def add_guide(user_id):
    #from junk_classify_module import classification
    user = User.query.get(user_id)

    if not user:
        return abort(404, description="User not found")
    
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')

        if content is None:
            return abort(400, description="content is required")

        #if classification.classify_message(content) == 1:
            #return abort(400, description="Junk content")

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
    return jsonify([{'id': guide.id, 'user_id': guide.user_id, 'title': guide.title, 'content': guide.content, 'latitude': guide.latitude, 'longitude': guide.longitude, 'created_at': guide.created_at, 'updated_at': guide.updated_at} for guide in guides]), 200

@app.route('/get_guides', methods=['GET'])
def get_guides():
    #guide = Guide.query.get(user_id)    #ガイドのidになってしまっている
    guides = Guide.query.all()
    if guides is None:
        return jsonify({'error': 'No guides found for this user'}), 404
    return jsonify([{'id': guide.id, 'user_id': guide.user_id, 'title': guide.title, 'content': guide.content, 'latitude': guide.latitude, 'longitude': guide.longitude} for guide in guides]), 200

@app.route('/get_userprofiles', methods=['GET'])
def get_userprofiles():
    userprofiles = UserProfile.query.all()
    userprofiles_list = [{'id': userprofile.id, 'userid': userprofile.user_id, 'bio': userprofile.bio, 'lang': userprofile.language} for userprofile in userprofiles]
    return jsonify(userprofiles_list), 200

@app.route('/add_like_dislike/<int:user_id>/<int:guide_id>', methods=['GET', 'POST'])
def add_like_dislike(user_id, guide_id):
    user = User.query.get(user_id)
    guide = Guide.query.get(guide_id)
    if not user:
        return abort(404, description="User not found")
    if not guide:
        return abort(404, description="Guide not found")
    if request.method == 'POST':
        status = request.form.get('status')
        if status is None:
            return abort(400, description="status is required")
        status_value = 0 if status == 'None' else 1 if status == 'Like' else -1
        existing_like_dislike = Like_Dislike.query.filter_by(user_id=user_id, guide_id=guide_id).first()
        if existing_like_dislike:
            existing_like_dislike.status = status_value
        else:
            new_like_dislike = Like_Dislike(user_id=user_id, guide_id=guide_id, status=status_value)
            db.session.add(new_like_dislike)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500
        return redirect(url_for('get_like_dislike', user_id=user_id, guide_id=guide_id))  # ここを修正
    return render_template('add_like_dislike.html', user_id=user_id, guide_id=guide_id)  

@app.route('/get_like_dislike/<int:user_id>', methods=['GET'])
def get_like_dislike(user_id):
    like_dislikes = Like_Dislike.query.filter_by(user_id=user_id).all()
    if like_dislikes is None:
        return jsonify({'error': 'No like_dislikes found for this user'}), 404
    return jsonify([{'id': like_dislike.id, 'user_id': like_dislike.user_id, 'guide_id': like_dislike.guide_id, 'status': like_dislike.status} for like_dislike in like_dislikes]), 200

# 以下、読み上げ機能部分
# ユーザーごとに読み上げたガイドをトラッキングする辞書
read_guides_by_user = {}

@app.route('/guide_voice', methods=['POST'])
def guide_voice():
    from guide_voice_module import voice
    from guide_voice_module import language_detect
    from guide_voice_module import translation_gpt
    from geopy.distance import geodesic

    data = request.get_json()
    current_lat = data.get('latitude')
    current_lng = data.get('longitude')
    user_id = data.get('user_id')
    userLang = data.get('userLang')
    #userLang = 'en'


    if current_lat is None or current_lng is None:
        return jsonify({'error': 'Latitude and longitude are required'}), 400

    recommended_spots = recommended_spots_by_user[user_id]
    #print(recommended_spots)

    # 初めてのユーザーの場合、読み上げ済みガイドリストを作成
    if user_id not in read_guides_by_user:
        read_guides_by_user[user_id] = []

    read_guides = read_guides_by_user[user_id]

    # 現在位置から最も近いガイドを見つける
    closest_guide = None
    min_distance = float('inf')
    current_location = (current_lat, current_lng)

    for spot in recommended_spots:
        #print(spot)
        if spot['name'] in read_guides:
            continue

        guide_location = (spot['lat'], spot['lng'])
        distance = geodesic(current_location, guide_location).meters
        if distance < min_distance:
            min_distance = distance
            closest_guide = spot
            #print(closest_guide)

    if closest_guide is None:
        return jsonify({'error': 'No new guides found'}), 404

    text = closest_guide['description']

    if language_detect.detect_language(text) == userLang:
        voice.text_to_speech(text, userLang)
        read_guides.append(closest_guide['name'])
        return jsonify({'message': 'Text processed without translation', 'guide': text})

    else:
        print("different language")
        prompt = f"Help me translate the sentence into '{userLang}'. Directly respond with the translation without any additional text.\\n{text}"

        # Place GPT API key here
        Translation = translation_gpt.Agent(model='gpt-4o', api_key="sk-proj-iVLzb4XmpgjatOIsfjCUT3BlbkFJWu6FAh5ZMJA0Drfs8Rth")
        response = Translation.communicate(prompt)

        voice.text_to_speech(response, userLang)
        read_guides.append(closest_guide['name'])
        return jsonify({'translated_text': response, 'guide': response})

# グローバル変数としてユーザーごとの推薦観光地リストを管理
recommended_spots_by_user = {}

#attractionsからではなく、Guideからデータを取ってくる。
def get_guide_data():
    guides = Guide.query.all()
    # フィールド名を変換する
    guides_list = [
        {
            'name': guide.title,
            'description': guide.content,
            'lat': guide.latitude,
            'lng': guide.longitude
        }
        for guide in guides
    ]
    return guides_list

@app.route('/reco', methods=['POST'])
def reco():
    from recommendation_module import recommendation
    from recommendation_module import user_profile_feature_extract
    import os

    data = request.get_json()
    user_id = data.get('user_id')
    print("useridは", user_id)
    user = User.query.filter_by(id=user_id).first()
    user_description = user.userprofile.bio
    print(user_description)
    print(type(user_description))
    like_dislike_records = user.like_dislike
    print(like_dislike_records)

    # データをuser_like_dislike形式に変換
    #そのユーザーのものを代入
    user_like_dislike = {}
    for record in like_dislike_records:
        guide = Guide.query.filter_by(id=record.guide_id).first()
        if guide:
            user_like_dislike[guide.title] = True if record.status == 1 else False

    print(user_like_dislike)

    # ユーザープロフィールと位置情報を用いて推薦された観光地を取得
    user_location = {'lng': data.get('longitude'), 'lat': data.get('latitude')}
    user_interests = user_profile_feature_extract.extract_interests(user_description, user_profile_feature_extract.INTEREST_CATEGORIES)

    user_profile_me = {
        'interests': user_interests,
        'like_dislike': user_like_dislike
    }

    # データベースからガイド情報を取得
    guide_data = get_guide_data()

    recommended_spots = recommendation.recommend_spots(user_location, user_profile_me, guide_data)

    # 推薦された観光地をユーザーごとのリストに保存
    recommended_spots_by_user[user_id] = recommended_spots

    print('おすすめスポット:',recommended_spots)

    return jsonify({'message': 'User logged in and recommendations calculated', 'recommended_spots': recommended_spots})

if __name__ == '__main__':
    with app.app_context():
        inspector = inspect(db.engine)
        print(inspector.get_table_names())
    app.run(debug=True)
