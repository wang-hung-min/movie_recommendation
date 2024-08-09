from flask import Flask, request, jsonify, send_from_directory
from flask import Flask, render_template
import pickle
import difflib
import requests


app = Flask(__name__)

# TMDb API 配置
TMDB_API_KEY = 'a862400f4750ec078c9ac26f1a71c392'
TMDB_API_URL = 'https://api.themoviedb.org/3'

# 載入推薦系統模型
with open('recommendation_model.pkl', 'rb') as file:
    model = pickle.load(file)

movies_data = model['movies_data']
similarity = model['similarity']

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/static/<path:path>')
def serve_static(path):
    return send_from_directory('static', path)

@app.route('/recommend', methods=['POST'])
def recommend():
    try:
        user_input = request.json.get('movie_name')
        if not user_input:
            return jsonify({"error": "No movie_name provided"}), 400

        list_of_all_titles = movies_data['original_title'].tolist()
        find_close_match = difflib.get_close_matches(user_input, list_of_all_titles)

        if not find_close_match:
            return jsonify({"error": "No close match found"}), 404

        close_match = find_close_match[0]
        index_of_the_movie = movies_data[movies_data['original_title'] == close_match]['index'].values[0]
        similarity_score = list(enumerate(similarity[index_of_the_movie]))
        sorted_similar_movies = sorted(similarity_score, key=lambda x: x[1], reverse=True)

        recommended_movies = []
        for movie in sorted_similar_movies[0:20]: 
            index = movie[0]
            title_from_index = movies_data[movies_data['index'] == index]['original_title'].values[0]
            recommended_movies.append(title_from_index)

        movie_details = []
        for title in recommended_movies:
            url = f'{TMDB_API_URL}/search/movie'
            params = {'api_key': TMDB_API_KEY, 'query': title}
            response = requests.get(url, params=params)
            data = response.json()
            if data['results']:
                movie = data['results'][0]
                movie_details.append({
                    'title': movie['title'],
                    'poster_path': movie.get('poster_path'),
                    'overview': movie.get('overview'),
                    'release_date': movie.get('release_date'),
                    'cast': get_movie_cast(movie['id'])
                })

        return jsonify(movie_details)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

def get_movie_cast(movie_id):
    url = f'{TMDB_API_URL}/movie/{movie_id}/credits'
    params = {'api_key': TMDB_API_KEY}
    response = requests.get(url, params=params)
    data = response.json()
    if 'cast' in data:
        return [member['name'] for member in data['cast'][:5]]  
    return []

if __name__ == '__main__':
    app.run(debug=True)