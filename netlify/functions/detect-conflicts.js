const { createClient } = require('@supabase/supabase-js');

const supabase = createClient(
  process.env.SUPABASE_URL,
  process.env.SUPABASE_KEY
);

// Keywords that indicate conflicting advice
const CONFLICT_KEYWORDS = {
  'api_security': {
    'good': ['environment variables', 'secure storage', 'never store in plain text', 'secret management'],
    'bad': ['plain text', 'config file', 'hardcode', 'source code']
  },
  'password_hashing': {
    'good': ['bcrypt', 'argon2', 'scrypt', 'secure hashing'],
    'bad': ['md5', 'sha1', 'plain text password']
  },
  'http_security': {
    'good': ['https', 'ssl', 'tls', 'encrypted'],
    'bad': ['http://', 'unencrypted', 'plain http']
  },
  'cookie_security': {
    'good': ['secure flag', 'httponly', 'samesite'],
    'bad': ['without secure', 'no security flags']
  },
  'file_upload': {
    'good': ['validation', 'sanitization', 'virus scan', 'type checking'],
    'bad': ['without validation', 'all file types', 'no restrictions']
  },
  'backup_security': {
    'good': ['encryption', 'secure storage', 'offsite backup'],
    'bad': ['without encryption', 'same server', 'unencrypted']
  },
  'sql_security': {
    'good': ['parameterized queries', 'prepared statements', 'orm'],
    'bad': ['concatenation', 'string concatenation', 'direct input']
  }
};

// Deprecated features and announcements
const DEPRECATED_FEATURES = [
  { feature: 'md5', deprecated_date: '2020-01-01', reason: 'Cryptographically broken' },
  { feature: 'sha1', deprecated_date: '2017-01-01', reason: 'Collision vulnerabilities' },
  { feature: 'http', deprecated_date: '2018-01-01', reason: 'Insecure protocol' },
  { feature: 'flash', deprecated_date: '2020-12-31', reason: 'End of life' },
  { feature: 'ftp', deprecated_date: '2019-01-01', reason: 'Insecure file transfer' }
];

function calculateConflictScore(article1, article2, category) {
  const keywords = CONFLICT_KEYWORDS[category];
  if (!keywords) return 0;

  const content1 = article1.content.toLowerCase();
  const content2 = article2.content.toLowerCase();

  let article1_good = 0, article1_bad = 0;
  let article2_good = 0, article2_bad = 0;

  // Count good and bad practices in each article
  keywords.good.forEach(keyword => {
    if (content1.includes(keyword)) article1_good++;
    if (content2.includes(keyword)) article2_good++;
  });

  keywords.bad.forEach(keyword => {
    if (content1.includes(keyword)) article1_bad++;
    if (content2.includes(keyword)) article2_bad++;
  });

  // Calculate conflict score (0-1)
  const article1_score = article1_good - article1_bad;
  const article2_score = article2_good - article2_bad;

  // High conflict if one is positive and other is negative
  if ((article1_score > 0 && article2_score < 0) || (article1_score < 0 && article2_score > 0)) {
    return Math.abs(article1_score - article2_score) / 10; // Normalize to 0-1
  }

  return 0;
}

function checkDeprecatedContent(article) {
  const content = article.content.toLowerCase();
  const deprecatedItems = [];

  DEPRECATED_FEATURES.forEach(item => {
    if (content.includes(item.feature)) {
      deprecatedItems.push({
        feature: item.feature,
        deprecated_date: item.deprecated_date,
        reason: item.reason,
        article_date: article.updated_at || article.created_at
      });
    }
  });

  return deprecatedItems;
}

function calculateRelevanceScore(article) {
  const now = new Date();
  const articleDate = new Date(article.updated_at || article.created_at);
  const daysSinceUpdate = (now - articleDate) / (1000 * 60 * 60 * 24);

  // Base relevance score (newer = more relevant)
  let relevanceScore = Math.max(0, 1 - (daysSinceUpdate / 365)); // Decreases over 1 year

  // Check for deprecated content
  const deprecatedItems = checkDeprecatedContent(article);
  if (deprecatedItems.length > 0) {
    relevanceScore *= 0.3; // Heavily penalize deprecated content
  }

  // Check version recency
  if (article.version) {
    const versionMatch = article.version.match(/(\d+)\.(\d+)/);
    if (versionMatch) {
      const majorVersion = parseInt(versionMatch[1]);
      const minorVersion = parseInt(versionMatch[2]);
      
      // Assume newer versions are more relevant
      if (majorVersion >= 3) relevanceScore *= 1.2;
      else if (majorVersion <= 1) relevanceScore *= 0.8;
    }
  }

  return Math.min(1, Math.max(0, relevanceScore));
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
    // Get all articles from database
    const { data: articles, error } = await supabase
      .from('kb_articles')
      .select('*')
      .order('updated_at', { ascending: false });

    if (error) throw error;

    if (!articles || articles.length < 2) {
      return {
        statusCode: 200,
        headers: {
          'Access-Control-Allow-Origin': '*',
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          conflicts: [],
          deprecated_articles: [],
          relevance_scores: [],
          message: 'Need at least 2 articles to detect conflicts'
        }),
      };
    }

    const conflicts = [];
    const deprecatedArticles = [];
    const relevanceScores = [];

    // Calculate relevance scores for all articles
    articles.forEach(article => {
      const relevanceScore = calculateRelevanceScore(article);
      const deprecatedItems = checkDeprecatedContent(article);
      
      relevanceScores.push({
        id: article.id,
        title: article.title,
        author: article.author,
        version: article.version,
        relevance_score: relevanceScore,
        last_updated: article.updated_at,
        deprecated_items: deprecatedItems,
        recommendation: relevanceScore < 0.3 ? 'HIGH PRIORITY: Needs immediate review/rewrite' :
                      relevanceScore < 0.6 ? 'MEDIUM PRIORITY: Should be updated' :
                      'LOW PRIORITY: Content appears current'
      });

      if (deprecatedItems.length > 0) {
        deprecatedArticles.push({
          id: article.id,
          title: article.title,
          deprecated_features: deprecatedItems,
          urgency: 'HIGH'
        });
      }
    });

    // Detect conflicts between articles
    for (let i = 0; i < articles.length; i++) {
      for (let j = i + 1; j < articles.length; j++) {
        const article1 = articles[i];
        const article2 = articles[j];

        // Check conflicts across all categories
        Object.keys(CONFLICT_KEYWORDS).forEach(category => {
          const conflictScore = calculateConflictScore(article1, article2, category);
          
          if (conflictScore > 0.3) { // Threshold for significant conflict
            conflicts.push({
              article1: {
                id: article1.id,
                title: article1.title,
                author: article1.author,
                version: article1.version
              },
              article2: {
                id: article2.id,
                title: article2.title,
                author: article2.author,
                version: article2.version
              },
              conflict_category: category,
              conflict_score: conflictScore,
              severity: conflictScore > 0.7 ? 'HIGH' : conflictScore > 0.5 ? 'MEDIUM' : 'LOW',
              recommendation: conflictScore > 0.7 ? 
                'CRITICAL: Articles provide contradictory advice - immediate resolution needed' :
                'WARNING: Articles may conflict - review and align recommendations'
            });
          }
        });
      }
    }

    // Sort by priority
    conflicts.sort((a, b) => b.conflict_score - a.conflict_score);
    relevanceScores.sort((a, b) => a.relevance_score - b.relevance_score);

    return {
      statusCode: 200,
      headers: {
        'Access-Control-Allow-Origin': '*',
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        summary: {
          total_articles: articles.length,
          conflicts_found: conflicts.length,
          deprecated_articles: deprecatedArticles.length,
          high_priority_updates: relevanceScores.filter(r => r.relevance_score < 0.3).length
        },
        conflicts: conflicts,
        deprecated_articles: deprecatedArticles,
        relevance_scores: relevanceScores,
        recommendations: {
          immediate_action: conflicts.filter(c => c.severity === 'HIGH').length + deprecatedArticles.length,
          review_needed: conflicts.filter(c => c.severity === 'MEDIUM').length + relevanceScores.filter(r => r.relevance_score < 0.6).length,
          total_kb_health_score: Math.round((1 - (conflicts.length + deprecatedArticles.length) / articles.length) * 100)
        }
      }),
    };
  } catch (error) {
    console.error('Error detecting conflicts:', error);
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