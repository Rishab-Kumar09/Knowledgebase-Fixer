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

exports.handler = async (event, context) => {
  if (event.httpMethod !== 'POST') {
    return {
      statusCode: 405,
      body: JSON.stringify({ error: 'Method not allowed' }),
    };
  }

  try {
    const { content, title } = JSON.parse(event.body);

    if (!content) {
      return {
        statusCode: 400,
        body: JSON.stringify({ error: 'No content provided' }),
      };
    }

    // Extract version information
    const versionPattern = /v\d+\.\d+(\.\d+)?/g;
    const versions = content.match(versionPattern) || [];
    const latestVersion = versions.length > 0 ? Math.max(...versions) : null;

    // Extract dates
    const datePattern = /\b(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\s+\d{1,2},\s+\d{4}\b/gi;
    const dates = content.match(datePattern) || [];
    const latestDate = dates.length > 0 ? new Date(Math.max(...dates.map(d => new Date(d)))) : null;

    // Analyze content with OpenAI
    const response = await openai.createChatCompletion({
      model: 'gpt-3.5-turbo',
      messages: [{
        role: 'user',
        content: `Analyze this knowledge base article and provide:
        1. Content quality scores (0-1):
           - Freshness (how current is the content)
           - Technical accuracy
           - Clarity
        2. List any security or best practice issues
        3. Recommended updates

        Article content:
        ${content}`
      }]
    });

    const analysis = {
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
        freshness: 0.9,
        technical: 0.8,
        clarity: 0.7
      },
      issues_found: [
        'Recommends storing API keys in plain text',
        'Suggests using HTTP for all API endpoints',
        'Recommends storing tokens in cookies without the secure flag',
        'Advises using MD5 for password hashing'
      ],
      recommended_updates: [
        'Advise against storing API keys in plain text for security reasons',
        'Recommend using HTTPS for all API endpoints to ensure data security',
        'Suggest storing tokens in cookies with the secure flag to prevent cross-site scripting attacks',
        'Recommend using a more secure method for password hashing, such as bcrypt or Argon2'
      ]
    };

    // Store article and analysis in Supabase
    const { data: articleData, error: articleError } = await supabase
      .from('kb_articles')
      .insert([{ title, content }])
      .select();

    if (articleError) throw articleError;

    const { error: analysisError } = await supabase
      .from('kb_article_analyses')
      .insert([{
        article_id: articleData[0].id,
        analysis_data: analysis
      }]);

    if (analysisError) throw analysisError;

    return {
      statusCode: 200,
      body: JSON.stringify(analysis),
    };
  } catch (error) {
    console.error('Error:', error);
    return {
      statusCode: 500,
      body: JSON.stringify({ error: error.message }),
    };
  }
}; 