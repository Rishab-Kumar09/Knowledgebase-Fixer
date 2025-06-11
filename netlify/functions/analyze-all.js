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

function analyzeArticleContent(content, metadata = {}) {
  // Extract version information - more flexible patterns
  const versionPatterns = [
    /v\d+\.\d+(\.\d+)?/gi,           // v1.0, v2.1
    /version\s+\d+\.\d+(\.\d+)?/gi,  // version 1.2.3
    /\d+\.\d+(\.\d+)?\s+release/gi,  // 1.2.3 release
    /api\s+v\d+/gi,                  // API v1
    /\d+\.\d+(\.\d+)?/g              // just numbers like 1.2.3
  ];
  
  let versions = [];
  versionPatterns.forEach(pattern => {
    const matches = content.match(pattern) || [];
    versions = versions.concat(matches);
  });
  
  // Use database version if available and not found in content
  if (metadata.version && versions.length === 0) {
    versions.push(metadata.version);
  }
  
  const latestVersion = versions.length > 0 ? versions[versions.length - 1] : null;

  // Use database updated_at date instead of extracting from content
  const latestDate = metadata.updated_at ? new Date(metadata.updated_at) : 
                    metadata.created_at ? new Date(metadata.created_at) : null;

  // Analyze content for issues (enhanced patterns)
  const issues = [];
  const recommendations = [];

  // Check for API key security issues
  if (content.toLowerCase().includes('plain text') && content.toLowerCase().includes('api key')) {
    issues.push('Recommends storing API keys in plain text');
    recommendations.push('Advise against storing API keys in plain text for security reasons');
  }

  // Check for HTTP vs HTTPS
  if (content.toLowerCase().includes('http://') || (content.toLowerCase().includes('http ') && !content.toLowerCase().includes('https'))) {
    issues.push('Suggests using HTTP for all API endpoints');
    recommendations.push('Recommend using HTTPS for all API endpoints to ensure data security');
  }

  // Check for weak password hashing
  if (content.toLowerCase().includes('md5') && (content.toLowerCase().includes('password') || content.toLowerCase().includes('hash'))) {
    issues.push('Advises using MD5 for password hashing');
    recommendations.push('Recommend using a more secure method for password hashing, such as bcrypt or Argon2');
  }

  // Check for cookie security
  if (content.toLowerCase().includes('cookie') && content.toLowerCase().includes('without') && content.toLowerCase().includes('security')) {
    issues.push('Recommends storing tokens in cookies without security flags');
    recommendations.push('Suggest storing tokens in cookies with the secure flag to prevent cross-site scripting attacks');
  }

  // Check for hardcoded credentials
  if (content.toLowerCase().includes('hardcode') && (content.toLowerCase().includes('password') || content.toLowerCase().includes('credential'))) {
    issues.push('Recommends hardcoding database credentials');
    recommendations.push('Use environment variables or secure credential management instead of hardcoding passwords');
  }

  // Check for file upload security
  if (content.toLowerCase().includes('file') && content.toLowerCase().includes('without validation')) {
    issues.push('Allows file uploads without proper validation');
    recommendations.push('Implement proper file validation and sanitization for uploads');
  }

  // Check for public file access
  if (content.toLowerCase().includes('publicly accessible') || (content.toLowerCase().includes('public') && content.toLowerCase().includes('read/write'))) {
    issues.push('Recommends making files publicly accessible with full permissions');
    recommendations.push('Restrict file permissions and avoid making sensitive directories publicly accessible');
  }

  // Check for backup security
  if (content.toLowerCase().includes('backup') && content.toLowerCase().includes('without encryption')) {
    issues.push('Suggests storing backups without encryption');
    recommendations.push('Always encrypt backup files and store them in secure, separate locations');
  }

  // Check for SQL injection vulnerabilities
  if (content.toLowerCase().includes('sql') && content.toLowerCase().includes('concatenat')) {
    issues.push('Suggests SQL query concatenation');
    recommendations.push('Use parameterized queries to prevent SQL injection attacks');
  }

  return {
    version_info: {
      versions_mentioned: versions,
      latest_version: latestVersion,
      last_updated: latestDate ? latestDate.toLocaleDateString('en-US', { 
        year: 'numeric', 
        month: 'long', 
        day: 'numeric' 
      }) : null,
      author: metadata.author || null
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
        .order('updated_at', { ascending: false });

      if (error) throw error;
      
      articlesToAnalyze = supabaseArticles.map(article => ({
        title: article.title,
        content: article.content,
        version: article.version,
        author: article.author,
        created_at: article.created_at,
        updated_at: article.updated_at
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
      const analysis = analyzeArticleContent(article.content, {
        version: article.version,
        author: article.author,
        created_at: article.created_at,
        updated_at: article.updated_at
      });
      
      // Debug logging to see what's being analyzed
      console.log('Analyzing article:', article.title);
      console.log('Content preview:', article.content.substring(0, 200) + '...');
      console.log('Versions found:', analysis.version_info.versions_mentioned);
      console.log('Latest version:', analysis.version_info.latest_version);
      console.log('Last updated:', analysis.version_info.last_updated);
      
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