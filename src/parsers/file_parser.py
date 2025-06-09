import logging
from pathlib import Path
from typing import Dict, List, Union
import frontmatter
from bs4 import BeautifulSoup
import markdown

logger = logging.getLogger(__name__)

class FileParser:
    """Parser for handling different types of KB article files."""
    
    def __init__(self):
        self.supported_extensions = {'.md', '.html', '.txt'}
    
    def parse_directory(self, directory: Union[str, Path]) -> List[Dict]:
        """Parse all supported files in the given directory."""
        directory = Path(directory)
        if not directory.exists():
            raise FileNotFoundError(f"Directory not found: {directory}")
        
        articles = []
        for file_path in directory.rglob('*'):
            if file_path.suffix in self.supported_extensions:
                try:
                    article = self.parse_file(file_path)
                    articles.append(article)
                except Exception as e:
                    logger.error(f"Error parsing {file_path}: {str(e)}")
        
        return articles
    
    def parse_file(self, file_path: Path) -> Dict:
        """Parse a single file based on its extension."""
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        content = file_path.read_text(encoding='utf-8')
        
        if file_path.suffix == '.md':
            return self._parse_markdown(content, file_path)
        elif file_path.suffix == '.html':
            return self._parse_html(content, file_path)
        else:  # .txt
            return self._parse_text(content, file_path)
    
    def _parse_markdown(self, content: str, file_path: Path) -> Dict:
        """Parse markdown content with frontmatter."""
        try:
            # Parse frontmatter if present
            post = frontmatter.loads(content)
            metadata = dict(post.metadata)
            
            # Convert markdown to plain text for analysis
            html = markdown.markdown(post.content)
            text = BeautifulSoup(html, 'html.parser').get_text()
            
            return {
                'path': str(file_path),
                'type': 'markdown',
                'metadata': metadata,
                'content': text,
                'raw_content': content
            }
        except Exception as e:
            logger.error(f"Error parsing markdown {file_path}: {str(e)}")
            raise
    
    def _parse_html(self, content: str, file_path: Path) -> Dict:
        """Parse HTML content."""
        try:
            soup = BeautifulSoup(content, 'html.parser')
            
            # Extract metadata from meta tags
            metadata = {}
            for meta in soup.find_all('meta'):
                name = meta.get('name')
                content = meta.get('content')
                if name and content:
                    metadata[name] = content
            
            # Get plain text content
            text = soup.get_text()
            
            return {
                'path': str(file_path),
                'type': 'html',
                'metadata': metadata,
                'content': text,
                'raw_content': content
            }
        except Exception as e:
            logger.error(f"Error parsing HTML {file_path}: {str(e)}")
            raise
    
    def _parse_text(self, content: str, file_path: Path) -> Dict:
        """Parse plain text content."""
        return {
            'path': str(file_path),
            'type': 'text',
            'metadata': {},
            'content': content,
            'raw_content': content
        } 