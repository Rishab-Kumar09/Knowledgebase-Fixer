from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()

supabase_url = os.environ.get("SUPABASE_URL")
supabase_key = os.environ.get("SUPABASE_KEY")

if not supabase_url or not supabase_key:
    raise ValueError("Missing Supabase configuration. Please set SUPABASE_URL and SUPABASE_KEY environment variables.")

supabase = create_client(supabase_url, supabase_key)

def store_article(title, content, version=None, author=None):
    """Store an article in Supabase."""
    return supabase.table('kb_articles').insert({
        'title': title,
        'content': content,
        'version': version,
        'author': author
    }).execute()

def get_all_articles():
    """Retrieve all articles from Supabase."""
    return supabase.table('kb_articles').select('*').execute()

def update_article_analysis(article_id, analysis_data):
    """Store analysis results for an article."""
    return supabase.table('kb_article_analyses').insert({
        'article_id': article_id,
        'analysis_data': analysis_data
    }).execute() 