from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import sys
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
        response = supabase.table('articles').select('*').order('created_at', desc=True).execute()
        return jsonify(response.data)
    except Exception as e:
        print(f"Error fetching articles: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/articles', methods=['POST'])
def create_article():
    try:
        data = request.json
        response = supabase.table('articles').insert({
            'title': data['title'],
            'content': data['content']
        }).execute()
        return jsonify(response.data[0])
    except Exception as e:
        print(f"Error creating article: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/analyze/<int:article_id>', methods=['POST'])
def analyze_article(article_id):
    try:
        # Get article from Supabase
        response = supabase.table('articles').select('content').eq('id', article_id).single().execute()
        if not response.data:
            return jsonify({"error": "Article not found"}), 404
        
        # Analyze the content
        content = response.data['content']
        analysis = analyze_content(content)
        
        # Store analysis in Supabase
        supabase.table('article_analyses').insert({
            'article_id': article_id,
            'analysis_data': analysis
        }).execute()
        
        return jsonify({"analysis": analysis})
    except Exception as e:
        print(f"Error analyzing article: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/analyze', methods=['POST'])
def analyze_new_content():
    try:
        data = request.json
        if not data or 'content' not in data:
            return jsonify({"error": "Content is required"}), 400
        
        analysis = analyze_content(data['content'])
        return jsonify({"analysis": analysis})
    except Exception as e:
        print(f"Error analyzing content: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True) 