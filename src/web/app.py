import os
import tempfile
from pathlib import Path
from flask import Flask, request, jsonify, render_template
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
import supabase
import json
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Load environment variables from the root directory
root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
dotenv_path = os.path.join(root_dir, '.env')
load_dotenv(dotenv_path)

# Import our analysis components
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from parsers.file_parser import FileParser, Article
from analyzer.content_analyzer import ContentAnalyzer
from reporter.report_generator import ReportGenerator

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Initialize our components
file_parser = FileParser()
content_analyzer = ContentAnalyzer()
report_generator = ReportGenerator()

# Initialize Supabase client
supabase_url = os.getenv('SUPABASE_URL')
supabase_key = os.getenv('SUPABASE_KEY')

if not supabase_url or not supabase_key:
    raise ValueError("Supabase URL and key must be set in environment variables")

try:
    supabase_client = supabase.create_client(supabase_url, supabase_key)
except Exception as e:
    logger.error(f"Failed to initialize Supabase client: {str(e)}")
    raise

def get_articles_from_db():
    """Fetch all articles from Supabase database."""
    try:
        response = supabase_client.table('kb_articles').select('*').execute()
        if not response.data:
            logger.warning("No articles found in database")
            return []
        return response.data
    except Exception as e:
        logger.error(f"Error fetching articles from database: {str(e)}")
        raise

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    if 'files' not in request.files:
        return jsonify({'error': 'No files uploaded'}), 400
    
    files = request.files.getlist('files')
    if not files:
        return jsonify({'error': 'No files selected'}), 400

    try:
        # Create temporary directory for uploaded files
        with tempfile.TemporaryDirectory() as temp_dir:
            # Save uploaded files
            for file in files:
                if file.filename:
                    filename = secure_filename(file.filename)
                    file_path = os.path.join(temp_dir, filename)
                    file.save(file_path)
            
            # Process articles
            articles = file_parser.parse_directory(temp_dir)
            
            # Analyze content
            analysis_results = content_analyzer.analyze_articles(articles)
            
            # Calculate summary statistics
            total_articles = len(analysis_results)
            articles_with_issues = sum(1 for r in analysis_results 
                                    if r.get('analysis') and r['analysis'].get('analysis', {}).get('issues'))
            scores = [r['analysis']['analysis'].get('score', 0) 
                     for r in analysis_results 
                     if r.get('analysis') and r['analysis'].get('analysis')]
            average_score = sum(scores) / len(scores) if scores else 0
            
            return jsonify({
                'total_articles': total_articles,
                'articles_with_issues': articles_with_issues,
                'average_score': average_score,
                'results': analysis_results
            })

    except Exception as e:
        logger.error(f"Error in analyze route: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/analyze-existing', methods=['POST'])
def analyze_existing():
    try:
        # Get articles from Supabase
        articles = get_articles_from_db()
        logger.info(f"Found {len(articles)} articles in database")
        
        # Convert to Article objects
        article_objects = []
        for article in articles:
            try:
                article_obj = Article(
                    path=article['title'],
                    content=article['content'],
                    metadata={'created_at': article['created_at']}
                )
                article_objects.append(article_obj)
                logger.debug(f"Converting article: {article['title']}")
            except Exception as e:
                logger.error(f"Error converting article {article['title']}: {str(e)}")
        
        # Analyze articles
        analyzer = ContentAnalyzer()
        results = analyzer.analyze_articles(article_objects)
        
        # Count articles with issues
        articles_with_issues = sum(1 for r in results if 'Issues:' in r['analysis']['analysis'])
        
        logger.info("Analysis complete")
        
        return jsonify({
            'total_articles': len(results),
            'articles_with_issues': articles_with_issues,
            'results': results
        })
        
    except Exception as e:
        logger.error(f"Error in analyze_existing: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Check for OpenAI API key
    if not os.getenv('OPENAI_API_KEY'):
        print('Error: OPENAI_API_KEY environment variable not set')
        print(f'Please make sure your API key is set in {dotenv_path}')
        sys.exit(1)
        
    app.run(debug=True) 