import logging
from typing import Dict, List
import openai
from tqdm import tqdm

logger = logging.getLogger(__name__)

class ContentAnalyzer:
    """Analyzes KB articles for issues using GPT."""
    
    def __init__(self):
        self.analysis_prompt = """You are reviewing a technical knowledgebase article.
The article below may be outdated or conflict with others.
If the information is wrong, outdated, or unclear, suggest an improved version.
Explain why the original content should be updated.

Article Metadata:
{metadata}

Article Content:
{content}

Please analyze the following aspects:
1. Content Accuracy
2. Technical Relevance
3. Clarity and Readability
4. Potential Conflicts
5. Suggested Updates

Provide your analysis in JSON format with the following structure:
{
    "score": float,  # 0-1 score for overall quality
    "issues": [
        {
            "type": str,  # "accuracy", "relevance", "clarity", "conflict"
            "severity": str,  # "low", "medium", "high"
            "description": str,
            "suggestion": str
        }
    ],
    "summary": str,  # Brief summary of findings
    "suggested_updates": str  # Proposed content updates
}"""

    def analyze_articles(self, articles: List[Dict]) -> List[Dict]:
        """Analyze a list of KB articles."""
        results = []
        
        for article in tqdm(articles, desc="Analyzing articles"):
            try:
                analysis = self._analyze_single_article(article)
                results.append({
                    'article': article,
                    'analysis': analysis
                })
            except Exception as e:
                logger.error(f"Error analyzing {article['path']}: {str(e)}")
                results.append({
                    'article': article,
                    'analysis': None,
                    'error': str(e)
                })
        
        return results
    
    def _analyze_single_article(self, article: Dict) -> Dict:
        """Analyze a single KB article using GPT."""
        try:
            # Prepare the prompt
            prompt = self.analysis_prompt.format(
                metadata=article['metadata'],
                content=article['content']
            )
            
            # Call GPT API
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a technical documentation expert."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,  # Lower temperature for more consistent analysis
                max_tokens=1000
            )
            
            # Extract and validate the analysis
            analysis = response.choices[0].message.content
            
            return {
                'raw_analysis': analysis,
                'timestamp': response.created
            }
            
        except Exception as e:
            logger.error(f"GPT analysis failed: {str(e)}")
            raise 