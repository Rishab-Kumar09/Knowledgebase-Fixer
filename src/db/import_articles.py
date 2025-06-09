import os
import sys
from pathlib import Path
from datetime import datetime

# Add the parent directory to the Python path
sys.path.append(str(Path(__file__).parent.parent))

from db.supabase_client import SupabaseManager
from parsers.file_parser import FileParser

def import_articles():
    """Import sample articles into Supabase."""
    try:
        # Initialize Supabase client
        supabase = SupabaseManager()
        file_parser = FileParser()
        
        # Get the examples directory
        examples_dir = Path(__file__).parent.parent.parent / 'examples'
        
        # Parse and import each article
        articles = file_parser.parse_directory(str(examples_dir))
        
        print(f"Found {len(articles)} articles to import:")
        for article in articles:
            try:
                # Extract version from content if available
                version = None
                if "Version:" in article['content']:
                    for line in article['content'].split('\n'):
                        if line.strip().startswith('- Version:'):
                            version = line.split(':')[1].strip()
                            break
                
                # Extract title from content
                title = article['content'].split('\n')[0].strip('# ')
                
                # Prepare article data
                article_data = {
                    'title': title,
                    'content': article['content'],
                    'type': article['type'],
                    'version': version,
                    'tags': ['installation', 'backup', 'configuration'] if 'installation' in article['path'].lower() else ['backup', 'configuration'],
                    'author': 'System',
                    'status': 'active',
                    'metadata': {
                        'original_file': str(article['path']),
                        'imported_at': datetime.now().isoformat()
                    }
                }
                
                # Import article
                result = supabase.create_article(article_data)
                if result:
                    print(f"✓ Imported: {article['path']}")
                else:
                    print(f"✗ Failed to import: {article['path']}")
            except Exception as e:
                print(f"✗ Error importing {article['path']}: {str(e)}")
        
        print("\nImport completed!")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    import_articles() 