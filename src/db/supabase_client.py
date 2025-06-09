from supabase import create_client, Client
import os
from typing import Dict, List, Optional
from datetime import datetime

class SupabaseManager:
    def __init__(self):
        supabase_url = os.getenv('SUPABASE_URL')
        supabase_key = os.getenv('SUPABASE_KEY')
        
        if not supabase_url or not supabase_key:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY environment variables are required")
        
        self.client: Client = create_client(supabase_url, supabase_key)
    
    def create_article(self, article: Dict) -> Dict:
        """Create a new knowledge base article."""
        data = {
            'title': article['title'],
            'content': article['content'],
            'type': article['type'],
            'version': article.get('version'),
            'tags': article.get('tags', []),
            'author': article.get('author'),
            'last_updated': datetime.now().isoformat(),
            'status': article.get('status', 'active'),
            'metadata': article.get('metadata', {})
        }
        
        response = self.client.table('kb_articles').insert(data).execute()
        return response.data[0] if response.data else None
    
    def update_article(self, article_id: str, updates: Dict) -> Dict:
        """Update an existing knowledge base article."""
        updates['last_updated'] = datetime.now().isoformat()
        response = self.client.table('kb_articles').update(updates).eq('id', article_id).execute()
        return response.data[0] if response.data else None
    
    def get_article(self, article_id: str) -> Optional[Dict]:
        """Get a single article by ID."""
        response = self.client.table('kb_articles').select('*').eq('id', article_id).execute()
        return response.data[0] if response.data else None
    
    def get_articles(self, filters: Optional[Dict] = None) -> List[Dict]:
        """Get multiple articles with optional filters."""
        query = self.client.table('kb_articles').select('*')
        
        if filters:
            if 'version' in filters:
                query = query.eq('version', filters['version'])
            if 'type' in filters:
                query = query.eq('type', filters['type'])
            if 'status' in filters:
                query = query.eq('status', filters['status'])
            if 'tags' in filters:
                query = query.contains('tags', filters['tags'])
        
        response = query.execute()
        return response.data if response.data else []
    
    def delete_article(self, article_id: str) -> bool:
        """Delete an article by ID."""
        response = self.client.table('kb_articles').delete().eq('id', article_id).execute()
        return bool(response.data)
    
    def search_articles(self, query: str) -> List[Dict]:
        """Search articles using full-text search."""
        response = self.client.rpc(
            'search_kb_articles',
            {'search_query': query}
        ).execute()
        return response.data if response.data else []
    
    def get_related_articles(self, article_id: str) -> List[Dict]:
        """Get articles related to the given article based on tags and content similarity."""
        response = self.client.rpc(
            'get_related_articles',
            {'article_id': article_id}
        ).execute()
        return response.data if response.data else []
    
    def execute_sql(self, sql: str) -> Dict:
        """Execute raw SQL statement."""
        return self.client.rpc('exec_sql', {'sql': sql}).execute() 