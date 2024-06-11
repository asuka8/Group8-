import json
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

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

if __name__ == '__main__':
    app.run(debug=True)
