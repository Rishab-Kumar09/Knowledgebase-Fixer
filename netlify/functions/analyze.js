const { OpenAI } = require('openai');
const { createClient } = require('@supabase/supabase-js');

// Initialize OpenAI client
const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY
});

// Initialize Supabase client
const supabase = createClient(
  process.env.SUPABASE_URL,
  process.env.SUPABASE_KEY
);

const ANALYSIS_PROMPT = `Analyze this knowledge base article and fill in this exact template:

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
{content}`;

async function analyzeArticle(content) {
  try {
    const response = await openai.chat.completions.create({
      model: "gpt-4",
      messages: [
        {
          role: "system",
          content: "You are a helpful assistant that analyzes knowledge base articles. Use the exact template provided, ensuring consistent formatting and number of items in lists."
        },
        {
          role: "user",
          content: ANALYSIS_PROMPT.replace("{content}", content || "No content provided")
        }
      ],
      temperature: 0.1
    });

    return {
      timestamp: new Date().toISOString(),
      analysis: response.choices[0].message.content.trim()
    };
  } catch (error) {
    console.error('Analysis failed:', error);
    return {
      timestamp: new Date().toISOString(),
      error: error.message,
      analysis: `VERSION INFORMATION
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
- Enhance clarity and structure`
    };
  }
}

exports.handler = async function(event, context) {
  // Set CORS headers
  const headers = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Access-Control-Allow-Methods': 'POST, OPTIONS',
    'Content-Type': 'application/json'
  };

  // Handle OPTIONS request for CORS
  if (event.httpMethod === 'OPTIONS') {
    return {
      statusCode: 204,
      headers
    };
  }

  // Only allow POST requests
  if (event.httpMethod !== 'POST') {
    return {
      statusCode: 405,
      headers,
      body: JSON.stringify({ error: 'Method not allowed' })
    };
  }

  try {
    // Get articles from Supabase
    const { data: articles, error: dbError } = await supabase
      .from('articles')
      .select('*');

    if (dbError) {
      console.error('Database error:', dbError);
      throw new Error('Failed to fetch articles from database');
    }

    if (!articles || articles.length === 0) {
      return {
        statusCode: 200,
        headers,
        body: JSON.stringify({
          total_articles: 0,
          articles_with_issues: 0,
          results: []
        })
      };
    }

    // Analyze each article
    const results = await Promise.all(
      articles.map(async (article) => {
        const result = await analyzeArticle(article.content);
        return {
          article_path: article.path,
          ...result
        };
      })
    );

    // Count articles with issues
    const articlesWithIssues = results.filter(result => {
      const analysis = result.analysis;
      return analysis.includes('ISSUES FOUND') && 
             analysis.split('ISSUES FOUND')[1].split('RECOMMENDED UPDATES')[0].trim() !== '';
    }).length;

    return {
      statusCode: 200,
      headers,
      body: JSON.stringify({
        total_articles: articles.length,
        articles_with_issues: articlesWithIssues,
        results: results
      })
    };
  } catch (error) {
    console.error('Function error:', error);
    return {
      statusCode: 500,
      headers,
      body: JSON.stringify({ 
        error: 'Internal server error',
        message: error.message
      })
    };
  }
} 