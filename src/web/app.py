from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
from ..db.setup_database import DatabaseManager
from ..analyzer.content_analyzer import analyze_content
import json

app = Flask(__name__, static_folder='../../public')
CORS(app)

# Initialize database manager
db = DatabaseManager(
    os.environ.get('SUPABASE_URL'),
    os.environ.get('SUPABASE_KEY')
)

@app.route('/')
def serve_static():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/api/articles', methods=['GET'])
def get_articles():
    """Get all articles from the database"""
    try:
        articles = db.get_all_articles()
        return jsonify(articles)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/articles/<article_id>', methods=['GET'])
def get_article(article_id):
    """Get a specific article by ID"""
    try:
        article = db.get_article_by_id(article_id)
        if not article:
            return jsonify({'error': 'Article not found'}), 404
        return jsonify(article)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/articles', methods=['POST'])
def create_article():
    """Create a new article from uploaded file or direct input"""
    try:
        if 'file' in request.files:
            file = request.files['file']
            content = file.read().decode('utf-8')
            title = file.filename
        else:
            data = request.get_json()
            content = data.get('content')
            title = data.get('title')

        if not content or not title:
            return jsonify({'error': 'Missing content or title'}), 400

        article = db.store_article(title, content)
        return jsonify(article), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/analyze/<article_id>', methods=['POST'])
def analyze_article(article_id):
    """Analyze an existing article"""
    try:
        article = db.get_article_by_id(article_id)
        if not article:
            return jsonify({'error': 'Article not found'}), 404

        analysis = analyze_content(article['content'])
        stored_analysis = db.store_analysis(article_id, analysis)
        return jsonify(stored_analysis)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/analyze', methods=['POST'])
def analyze_new_content():
    """Analyze content without storing it"""
    try:
        data = request.get_json()
        content = data.get('content')
        if not content:
            return jsonify({'error': 'Missing content'}), 400

        analysis = analyze_content(content)
        return jsonify(analysis)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True) 