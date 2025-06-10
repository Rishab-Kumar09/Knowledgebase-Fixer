from supabase import create_client
import os
from typing import Dict, List, Optional
from datetime import datetime

def get_supabase_client():
    """Create and return a Supabase client using environment variables"""
    supabase_url = os.environ.get('SUPABASE_URL')
    supabase_key = os.environ.get('SUPABASE_KEY')
    
    if not supabase_url or not supabase_key:
        raise ValueError("SUPABASE_URL and SUPABASE_KEY environment variables must be set")
    
    return create_client(supabase_url, supabase_key)

class DatabaseManager:
    def __init__(self, supabase_url: str, supabase_key: str):
        self.supabase = create_client(supabase_url, supabase_key)

    def get_all_articles(self) -> List[Dict]:
        """Get all articles from the database"""
        response = self.supabase.table('kb_articles').select('*').order('created_at', desc=True).execute()
        return response.data

    def get_article_by_id(self, article_id: str) -> Optional[Dict]:
        """Get a specific article by ID"""
        response = self.supabase.table('kb_articles').select('*').eq('id', article_id).single().execute()
        return response.data if response.data else None

    def store_article(self, title: str, content: str, type: str = 'general', version: str = None, 
                     tags: List[str] = None, author: str = None, metadata: Dict = None) -> Dict:
        """Store a new article in the database"""
        article_data = {
            'title': title,
            'content': content,
            'type': type,
            'version': version,
            'tags': tags or [],
            'author': author,
            'metadata': metadata or {},
            'status': 'active'
        }
        response = self.supabase.table('kb_articles').insert(article_data).execute()
        return response.data[0]

    def update_article(self, article_id: str, updates: Dict) -> Dict:
        """Update an existing article"""
        updates['last_updated'] = datetime.utcnow().isoformat()
        response = self.supabase.table('kb_articles').update(updates).eq('id', article_id).execute()
        return response.data[0]

    def search_articles(self, query: str) -> List[Dict]:
        """Search articles using the full-text search function"""
        response = self.supabase.rpc('search_kb_articles', {'search_query': query}).execute()
        return response.data

    def get_related_articles(self, article_id: str) -> List[Dict]:
        """Get related articles using the similarity function"""
        response = self.supabase.rpc('get_related_articles', {'article_id': article_id}).execute()
        return response.data

    def store_analysis(self, article_id: str, analysis_data: Dict) -> Dict:
        """Store analysis results in the article's metadata"""
        metadata = {'analysis': analysis_data, 'analyzed_at': datetime.utcnow().isoformat()}
        return self.update_article(article_id, {'metadata': metadata})

    def get_article_history(self, article_id: str) -> List[Dict]:
        """Get the history of changes for an article"""
        response = self.supabase.table('kb_article_history').select('*').eq('article_id', article_id).order('performed_at', desc=True).execute()
        return response.data 