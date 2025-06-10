from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import sys
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables from .env file
load_dotenv()

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from analyzer.content_analyzer import analyze_content
from db.setup_database import get_supabase_client

app = Flask(__name__, static_folder='../../public')
CORS(app)

# Initialize Supabase client
supabase = get_supabase_client()

@app.route('/')
def serve_index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/api/articles', methods=['GET'])
def get_articles():
    try:
        response = supabase.table('kb_articles').select('*').order('created_at', desc=True).execute()
        return jsonify(response.data)
    except Exception as e:
        print(f"Error fetching articles: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/articles/search', methods=['GET'])
def search_articles():
    try:
        query = request.args.get('q', '')
        response = supabase.rpc('search_kb_articles', {'search_query': query}).execute()
        return jsonify(response.data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/articles/<article_id>/related', methods=['GET'])
def get_related_articles(article_id):
    try:
        response = supabase.rpc('get_related_articles', {'article_id': article_id}).execute()
        return jsonify(response.data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/articles', methods=['POST'])
def create_article():
    try:
        data = request.json
        required_fields = ['title', 'content', 'type']
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400

        article_data = {
            'title': data['title'],
            'content': data['content'],
            'type': data['type'],
            'version': data.get('version'),
            'tags': data.get('tags', []),
            'author': data.get('author'),
            'metadata': data.get('metadata', {}),
            'status': 'active'
        }

        response = supabase.table('kb_articles').insert(article_data).execute()
        return jsonify(response.data[0])
    except Exception as e:
        print(f"Error creating article: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/articles/<article_id>', methods=['PUT'])
def update_article(article_id):
    try:
        data = request.json
        response = supabase.table('kb_articles').update(data).eq('id', article_id).execute()
        return jsonify(response.data[0])
    except Exception as e:
        print(f"Error updating article: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/articles/<article_id>/analyze', methods=['POST'])
def analyze_article(article_id):
    try:
        # Get the article
        article = supabase.table('kb_articles').select('*').eq('id', article_id).single().execute()
        if not article.data:
            return jsonify({'error': 'Article not found'}), 404

        # Analyze the content
        analysis_result = analyze_content(article.data['content'])
        
        # Store analysis in metadata
        metadata = article.data.get('metadata', {})
        metadata['analysis'] = analysis_result
        metadata['analyzed_at'] = datetime.utcnow().isoformat()
        
        # Update the article
        response = supabase.table('kb_articles').update({'metadata': metadata}).eq('id', article_id).execute()
        return jsonify({'analysis': analysis_result})
    except Exception as e:
        print(f"Error analyzing article: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/articles/<article_id>/history', methods=['GET'])
def get_article_history(article_id):
    try:
        response = supabase.table('kb_article_history').select('*').eq('article_id', article_id).order('performed_at', desc=True).execute()
        return jsonify(response.data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True) 