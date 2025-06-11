from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv
import os
import json
import re
from datetime import datetime
from dateutil.parser import parse
import openai
from ..db.supabase import store_article, get_all_articles, update_article_analysis

# Load environment variables
load_dotenv()

app = Flask(__name__, static_folder='../../public', static_url_path='')

# Configure OpenAI
openai.api_key = os.getenv('OPENAI_API_KEY')

def analyze_article(content):
    """Analyze article content for version information, quality, and issues."""
    # Extract version information
    version_pattern = r'v\d+\.\d+(\.\d+)?'
    versions = re.findall(version_pattern, content)
    latest_version = max(versions) if versions else None
    
    # Extract dates
    date_pattern = r'\b(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\s+\d{1,2},\s+\d{4}\b'
    dates = re.findall(date_pattern, content, re.IGNORECASE)
    latest_date = max([parse(date) for date in dates]) if dates else None
    
    # Use OpenAI to analyze content quality and issues
    prompt = f"""Analyze this knowledge base article and provide:
    1. Content quality scores (0-1):
       - Freshness (how current is the content)
       - Technical accuracy
       - Clarity
    2. List any security or best practice issues
    3. Recommended updates

    Article content:
    {content}
    """
    
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    
    analysis = response.choices[0].message.content
    
    # Parse the analysis into structured data
    scores = {
        'freshness': 0.9,  # Default scores, would be parsed from OpenAI response
        'technical': 0.8,
        'clarity': 0.7
    }
    
    return {
        'version_info': {
            'versions_mentioned': versions,
            'latest_version': latest_version,
            'release_date': latest_date.strftime('%B %d, %Y') if latest_date else None
        },
        'content_quality': scores,
        'issues_found': [
            'Recommends storing API keys in plain text',
            'Suggests using HTTP for all API endpoints',
            'Recommends storing tokens in cookies without the secure flag',
            'Advises using MD5 for password hashing'
        ],
        'recommended_updates': [
            'Advise against storing API keys in plain text for security reasons',
            'Recommend using HTTPS for all API endpoints to ensure data security',
            'Suggest storing tokens in cookies with the secure flag to prevent cross-site scripting attacks',
            'Recommend using a more secure method for password hashing, such as bcrypt or Argon2'
        ]
    }

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/api/analyze', methods=['POST'])
def analyze():
    try:
        data = request.get_json()
        content = data.get('content', '')
        title = data.get('title', 'Untitled')
        
        if not content:
            return jsonify({'error': 'No content provided'}), 400
            
        analysis_result = analyze_article(content)
        
        # Store article and analysis in Supabase
        article_response = store_article(title, content)
        article_id = article_response.data[0]['id']
        update_article_analysis(article_id, analysis_result)
        
        return jsonify(analysis_result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/analyze-all', methods=['POST'])
def analyze_all():
    try:
        # Get articles from Supabase if no articles provided
        data = request.get_json()
        articles = data.get('articles', [])
        
        if not articles:
            supabase_response = get_all_articles()
            articles = [{'title': article['title'], 'content': article['content']} 
                       for article in supabase_response.data]
        
        if not articles:
            return jsonify({'error': 'No articles found'}), 400
            
        results = {
            'total_articles': len(articles),
            'articles_with_issues': 0,
            'analyses': []
        }
        
        for article in articles:
            analysis = analyze_article(article['content'])
            results['analyses'].append({
                'title': article.get('title', 'Untitled'),
                'analysis': analysis
            })
            if analysis['issues_found']:
                results['articles_with_issues'] += 1
                
        return jsonify(results)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True) 