import json
import logging
from pathlib import Path
from typing import Dict, List
from datetime import datetime
import jinja2

logger = logging.getLogger(__name__)

class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

class ReportGenerator:
    """Generates analysis reports in various formats."""
    
    def __init__(self):
        self.markdown_template = """# Knowledge Base Analysis Report
## Summary {{ timestamp }}
Total Articles Analyzed: {{ total_articles }}
Articles with Issues: {{ articles_with_issues }}
Average Quality Score: {{ average_score }}

## Detailed Analysis

{% for result in results %}
### {{ result.article.path }}
**Type**: {{ result.article.type }}
**Quality Score**: {% if result.analysis and result.analysis.analysis %}{{ result.analysis.analysis.score }}{% endif %}

#### Issues Found:
{% if result.analysis and result.analysis.analysis and result.analysis.analysis.issues %}
{% for issue in result.analysis.analysis.issues %}
* **{{ issue.type|title }}** (Severity: {{ issue.severity }})
  - {{ issue.description }}
  - Suggestion: {{ issue.suggestion }}
{% endfor %}
{% endif %}

#### Summary:
{% if result.analysis and result.analysis.analysis %}{{ result.analysis.analysis.summary }}{% endif %}

#### Suggested Updates:
```
{% if result.analysis and result.analysis.analysis %}{{ result.analysis.analysis.suggested_updates }}{% endif %}
```

---
{% endfor %}"""

        self.html_template = """<!DOCTYPE html>
<html>
<head>
    <title>Knowledge Base Analysis Report</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 2em; }
        .article { margin-bottom: 2em; padding: 1em; border: 1px solid #ddd; }
        .issue { margin: 1em 0; padding: 0.5em; background: #f9f9f9; }
        .high { border-left: 4px solid #ff4444; }
        .medium { border-left: 4px solid #ffbb33; }
        .low { border-left: 4px solid #00C851; }
    </style>
</head>
<body>
    <h1>Knowledge Base Analysis Report</h1>
    <p>Generated: {{ timestamp }}</p>

    <h2>Summary</h2>
    <ul>
        <li>Total Articles Analyzed: {{ total_articles }}</li>
        <li>Articles with Issues: {{ articles_with_issues }}</li>
        <li>Average Quality Score: {{ average_score }}</li>
    </ul>

    <h2>Detailed Analysis</h2>
    {% for result in results %}
    <div class="article">
        <h3>{{ result.article.path }}</h3>
        <p><strong>Type:</strong> {{ result.article.type }}</p>
        <p><strong>Quality Score:</strong> {% if result.analysis and result.analysis.analysis %}{{ result.analysis.analysis.score }}{% endif %}</p>

        <h4>Issues Found:</h4>
        {% if result.analysis and result.analysis.analysis and result.analysis.analysis.issues %}
        {% for issue in result.analysis.analysis.issues %}
        <div class="issue {{ issue.severity }}">
            <strong>{{ issue.type|title }}</strong> (Severity: {{ issue.severity }})
            <p>{{ issue.description }}</p>
            <p><em>Suggestion:</em> {{ issue.suggestion }}</p>
        </div>
        {% endfor %}
        {% endif %}

        <h4>Summary:</h4>
        <p>{% if result.analysis and result.analysis.analysis %}{{ result.analysis.analysis.summary }}{% endif %}</p>

        <h4>Suggested Updates:</h4>
        <pre>{% if result.analysis and result.analysis.analysis %}{{ result.analysis.analysis.suggested_updates }}{% endif %}</pre>
    </div>
    {% endfor %}
</body>
</html>
"""

    def generate_report(self, results: List[Dict], output_dir: Path, format: str = 'markdown'):
        """Generate a report from analysis results."""
        try:
            # Calculate summary statistics
            total_articles = len(results)
            articles_with_issues = sum(1 for r in results if r.get('analysis') and r['analysis'].get('analysis', {}).get('issues'))
            scores = [r['analysis']['analysis'].get('score', 0) for r in results if r.get('analysis') and r['analysis'].get('analysis')]
            average_score = sum(scores) / len(scores) if scores else 0
            
            # Prepare template data
            template_data = {
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'total_articles': total_articles,
                'articles_with_issues': articles_with_issues,
                'average_score': f"{average_score:.2f}",
                'results': results
            }
            
            # Generate report using appropriate template
            template_str = self.markdown_template if format == 'markdown' else self.html_template
            template = jinja2.Template(template_str)
            report_content = template.render(**template_data)
            
            # Save report
            output_file = output_dir / f"report.{'md' if format == 'markdown' else 'html'}"
            output_file.write_text(report_content, encoding='utf-8')
            
            # Save raw results as JSON for further processing if needed
            json_file = output_dir / 'analysis_results.json'
            with json_file.open('w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, cls=DateTimeEncoder)
            
            logger.info(f"Report generated: {output_file}")
            logger.info(f"Raw results saved: {json_file}")
            
        except Exception as e:
            logger.error(f"Error generating report: {str(e)}")
            raise 