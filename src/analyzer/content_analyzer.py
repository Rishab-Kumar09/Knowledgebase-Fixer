import os
from openai import OpenAI
from typing import Dict, Any

client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))

def analyze_content(content: str) -> Dict[str, Any]:
    """
    Analyze article content using OpenAI's GPT model.
    Returns a structured analysis of the content.
    """
    prompt = f"""
    Analyze the following knowledge base article and provide a detailed assessment.
    Focus on the following aspects:
    1. Content quality and accuracy
    2. Technical accuracy and completeness
    3. Structure and organization
    4. SEO optimization
    5. Improvement recommendations

    Article content:
    {content}

    Provide the analysis in the following JSON structure:
    {{
        "overall_score": (1-10),
        "clarity_score": (1-10),
        "technical_accuracy_score": (1-10),
        "completeness_score": (1-10),
        "summary": "Brief summary of the article",
        "technical_updates": ["List of technical aspects that need updating"],
        "improvement_suggestions": ["List of specific improvements needed"],
        "seo_recommendations": ["List of SEO optimization suggestions"]
    }}
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a technical documentation expert specializing in knowledge base article analysis."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )

        # Parse the response
        analysis = response.choices[0].message.content
        return analysis

    except Exception as e:
        print(f"Error in content analysis: {str(e)}")
        raise Exception("Failed to analyze content") 