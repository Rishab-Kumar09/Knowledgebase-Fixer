from supabase import create_client
import os
from typing import Dict, List, Optional

class DatabaseManager:
    def __init__(self, supabase_url: str, supabase_key: str):
        self.supabase = create_client(supabase_url, supabase_key)
        self._init_tables()

    def _init_tables(self):
        # Tables are created through Supabase dashboard
        # This is just a placeholder for any initialization if needed
        pass

    def get_all_articles(self) -> List[Dict]:
        """Get all articles from the database"""
        response = self.supabase.table('articles').select('*').execute()
        return response.data

    def get_article_by_id(self, article_id: str) -> Optional[Dict]:
        """Get a specific article by ID"""
        response = self.supabase.table('articles').select('*').eq('id', article_id).execute()
        return response.data[0] if response.data else None

    def store_article(self, title: str, content: str, metadata: Dict = None) -> Dict:
        """Store a new article in the database"""
        article_data = {
            'title': title,
            'content': content,
            'metadata': metadata or {}
        }
        response = self.supabase.table('articles').insert(article_data).execute()
        return response.data[0]

    def store_analysis(self, article_id: str, analysis_data: Dict) -> Dict:
        """Store analysis results for an article"""
        analysis = {
            'article_id': article_id,
            'analysis_data': analysis_data,
            'created_at': 'now()'
        }
        response = self.supabase.table('article_analyses').insert(analysis).execute()
        return response.data[0]

    def get_article_analyses(self, article_id: str) -> List[Dict]:
        """Get all analyses for a specific article"""
        response = self.supabase.table('article_analyses').select('*').eq('article_id', article_id).execute()
        return response.data 