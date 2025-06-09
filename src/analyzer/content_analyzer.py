import logging
import json
from typing import Dict, List, Optional
from openai import OpenAI
from tqdm import tqdm
import os
from datetime import datetime
import re
import httpx

logger = logging.getLogger(__name__)

class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

class ContentAnalyzer:
    """Analyzer for knowledge base articles with conflict detection and version awareness."""
    
    def __init__(self):
        """Initialize the analyzer with OpenAI client."""
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OpenAI API key not found in environment variables")
        
        # Initialize OpenAI client with custom http client to avoid proxy issues
        http_client = httpx.Client()
        self.client = OpenAI(
            api_key=api_key,
            http_client=http_client
        )
        
        # Simple template-based prompt with clearer version info
        self.analysis_prompt = """Analyze this knowledge base article and fill in this exact template:

VERSION INFORMATION
Versions Mentioned: [list all version numbers found]
Latest Version: [specify the most recent version based on release dates and status mentions]
Release Date: [date of the latest version, if found, otherwise "Not specified"]

CONTENT QUALITY
Freshness Score: [0-1]
Technical Score: [0-1]
Clarity Score: [0-1]

ISSUES FOUND
[list exactly 4 most important issues, one per line with a dash]
- [Issue 1]
- [Issue 2]
- [Issue 3]
- [Issue 4]

RECOMMENDED UPDATES
[list exactly 4 most important improvements, one per line with a dash]
- [Update 1]
- [Update 2]
- [Update 3]
- [Update 4]

Article Content:
{content}

Fill in the template above, keeping the exact headers and format. For version information, check release dates and status mentions."""
    
    def analyze_articles(self, articles: List[Dict]) -> List[Dict]:
        """
        Analyze a list of articles for quality and conflicts.
        
        Args:
            articles: List of Article objects to analyze
            
        Returns:
            List of analysis results for each article
        """
        results = []
        
        # First pass - collect all version information
        version_info = {}
        for article in articles:
            try:
                versions = self._extract_versions(article.content)
                for version in versions:
                    if version not in version_info:
                        version_info[version] = {
                            'mentioned_in': [],
                            'dates': [],
                            'status': []
                        }
                    version_info[version]['mentioned_in'].append(article.path)
                    
                    # Extract dates
                    dates = re.findall(r'\d{4}-\d{2}-\d{2}', article.content)
                    version_info[version]['dates'].extend(dates)
                    
                    # Extract status mentions
                    status_matches = re.findall(r'(?:status|version).*?(?:active|deprecated|supported|unsupported)', 
                                             article.content.lower())
                    version_info[version]['status'].extend(status_matches)
            except Exception as e:
                logger.error(f"Error extracting version info from {article.path}: {str(e)}")

        # Second pass - analyze articles with version context
        for article in articles:
            try:
                result = self._analyze_single_article(article, version_info)
                results.append({
                    'article_path': article.path,
                    'analysis': result
                })
            except Exception as e:
                logger.error(f"Error analyzing article {article.path}: {str(e)}")
                results.append({
                    'article_path': article.path,
                    'analysis': self._get_default_analysis()
                })
        
        return results
    
    def _extract_versions(self, content: str) -> List[str]:
        """Extract version numbers from content."""
        version_pattern = r'v?\d+\.\d+(\.\d+)?'
        versions = re.findall(version_pattern, content)
        return list(set(versions))
    
    def _analyze_single_article(self, article, version_info=None) -> Dict:
        """Analyze a single article using GPT."""
        try:
            # Add version context to the prompt if available
            context = ""
            if version_info:
                context = "\nVersion Context:\n"
                for version, info in version_info.items():
                    context += f"Version {version}:\n"
                    if info['dates']:
                        context += f"- Dates mentioned: {', '.join(info['dates'])}\n"
                    if info['status']:
                        context += f"- Status mentions: {', '.join(info['status'])}\n"

            # Call GPT API
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that analyzes knowledge base articles. Use the exact template provided, ensuring consistent formatting and number of items in lists."},
                    {"role": "user", "content": self.analysis_prompt.format(content=article.content + context)}
                ],
                temperature=0.1
            )

            # Get the response text
            analysis_text = response.choices[0].message.content.strip()
            
            return {
                'timestamp': datetime.now().isoformat(),
                'analysis': analysis_text
            }

        except Exception as e:
            logger.error(f"GPT analysis failed: {str(e)}")
            return self._get_default_analysis()
    
    def _get_default_analysis(self) -> Dict:
        """Return a default analysis structure when analysis fails."""
        return {
            'timestamp': datetime.now().isoformat(),
            'analysis': """VERSION INFORMATION
Versions Mentioned: None found
Latest Version: Unknown
Release Date: Not specified

CONTENT QUALITY
Freshness Score: 0.5
Technical Score: 0.5
Clarity Score: 0.5

ISSUES FOUND
- Failed to analyze content
- Content analysis incomplete
- Version information missing
- Quality assessment needed

RECOMMENDED UPDATES
- Review and update content
- Add version information
- Improve technical accuracy
- Enhance clarity and structure"""
        }
    
    def _extract_key_info(self, article: Dict) -> Dict:
        """Extract key information from an article for conflict detection."""
        # Extract version numbers
        version_pattern = r'v?\d+\.\d+(\.\d+)?'
        versions = re.findall(version_pattern, article['content'])
        
        # Extract key technical terms
        technical_terms = self._extract_technical_terms(article['content'])
        
        return {
            'versions': versions,
            'technical_terms': technical_terms,
            'type': article['type'],
            'metadata': article['metadata']
        }
    
    def _extract_technical_terms(self, content: str) -> List[str]:
        """Extract technical terms and concepts from content."""
        # Basic technical term extraction
        term_patterns = [
            r'(?i)api\s+\w+',
            r'(?i)endpoint\s+[\w/]+',
            r'(?i)command\s+[\w-]+',
            r'(?i)config\s+[\w-]+',
            r'(?i)setting\s+[\w-]+'
        ]
        
        terms = []
        for pattern in term_patterns:
            terms.extend(re.findall(pattern, content))
        return list(set(terms))
    
    def _prepare_context_summary(self, other_contexts: Dict) -> str:
        """Prepare a summary of other articles for conflict detection."""
        summary_parts = []
        for path, context in other_contexts.items():
            summary = f"Article {path}:\n"
            summary += f"- Versions mentioned: {', '.join(context['versions'])}\n"
            summary += f"- Technical terms: {', '.join(context['technical_terms'])}\n"
            summary_parts.append(summary)
        
        return "\n".join(summary_parts) 