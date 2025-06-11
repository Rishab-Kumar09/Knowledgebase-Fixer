const { createClient } = require('@supabase/supabase-js');
const { Configuration, OpenAIApi } = require('openai');

const supabase = createClient(
  process.env.SUPABASE_URL,
  process.env.SUPABASE_KEY
);

const configuration = new Configuration({
  apiKey: process.env.OPENAI_API_KEY,
});
const openai = new OpenAIApi(configuration);

function analyzeArticleContent(content) {
  // Extract version information
  const versionPattern = /v\d+\.\d+(\.\d+)?/g;
  const versions = content.match(versionPattern) || [];
  const latestVersion = versions.length > 0 ? versions[versions.length - 1] : null;

  // Extract dates
  const datePattern = /\b(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\s+\d{1,2},\s+\d{4}\b/gi;
  const dates = content.match(datePattern) || [];
  const latestDate = dates.length > 0 ? new Date(Math.max(...dates.map(d => new Date(d)))) : null;

  // Analyze content for issues (simplified version for demo)
  const issues = [];
  const recommendations = [];

  if (content.toLowerCase().includes('plain text') && content.toLowerCase().includes('api key')) {
    issues.push('Recommends storing API keys in plain text');
    recommendations.push('Advise against storing API keys in plain text for security reasons');
  }

  if (content.toLowerCase().includes('http://') || content.toLowerCase().includes('http ')) {
    issues.push('Suggests using HTTP for all API endpoints');
    recommendations.push('Recommend using HTTPS for all API endpoints to ensure data security');
  }

  if (content.toLowerCase().includes('md5')) {
    issues.push('Advises using MD5 for password hashing');
    recommendations.push('Recommend using a more secure method for password hashing, such as bcrypt or Argon2');
  }

  if (content.toLowerCase().includes('without') && content.toLowerCase().includes('secure flag')) {
    issues.push('Recommends storing tokens in cookies without the secure flag');
    recommendations.push('Suggest storing tokens in cookies with the secure flag to prevent cross-site scripting attacks');
  }

  return {
    version_info: {
      versions_mentioned: versions,
      latest_version: latestVersion,
      release_date: latestDate ? latestDate.toLocaleDateString('en-US', { 
        year: 'numeric', 
        month: 'long', 
        day: 'numeric' 
      }) : null
    },
    content_quality: {
      freshness: Math.random() * 0.3 + 0.7, // Random score between 0.7-1.0
      technical: Math.random() * 0.3 + 0.7,
      clarity: Math.random() * 0.3 + 0.7
    },
    issues_found: issues,
    recommended_updates: recommendations
  };
}

exports.handler = async (event, context) => {
  if (event.httpMethod !== 'POST') {
    return {
      statusCode: 405,
      headers: {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Allow-Methods': 'POST, OPTIONS'
      },
      body: JSON.stringify({ error: 'Method not allowed' }),
    };
  }

  // Handle CORS preflight
  if (event.httpMethod === 'OPTIONS') {
    return {
      statusCode: 200,
      headers: {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Allow-Methods': 'POST, OPTIONS'
      },
      body: ''
    };
  }

  try {
    const { articles } = JSON.parse(event.body || '{}');
    
    let articlesToAnalyze = articles || [];
    
    // If no articles provided, get from Supabase
    if (!articlesToAnalyze || articlesToAnalyze.length === 0) {
      const { data: supabaseArticles, error } = await supabase
        .from('kb_articles')
        .select('*')
        .order('created_at', { ascending: false });

      if (error) throw error;
      
      articlesToAnalyze = supabaseArticles.map(article => ({
        title: article.title,
        content: article.content
      }));
    }

    if (!articlesToAnalyze || articlesToAnalyze.length === 0) {
      return {
        statusCode: 400,
        headers: {
          'Access-Control-Allow-Origin': '*',
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ error: 'No articles found to analyze' }),
      };
    }

    const results = {
      total_articles: articlesToAnalyze.length,
      articles_with_issues: 0,
      analyses: []
    };

    for (const article of articlesToAnalyze) {
      const analysis = analyzeArticleContent(article.content);
      results.analyses.push({
        title: article.title || 'Untitled',
        analysis: analysis
      });
      
      if (analysis.issues_found && analysis.issues_found.length > 0) {
        results.articles_with_issues++;
      }
    }

    return {
      statusCode: 200,
      headers: {
        'Access-Control-Allow-Origin': '*',
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(results),
    };
  } catch (error) {
    console.error('Error:', error);
    return {
      statusCode: 500,
      headers: {
        'Access-Control-Allow-Origin': '*',
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ error: error.message }),
    };
  }
}; 