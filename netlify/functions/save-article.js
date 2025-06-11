const { createClient } = require('@supabase/supabase-js');

const supabase = createClient(
  process.env.SUPABASE_URL,
  process.env.SUPABASE_KEY
);

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
    const { title, content, analysis } = JSON.parse(event.body || '{}');
    
    if (!title || !content) {
      return {
        statusCode: 400,
        headers: {
          'Access-Control-Allow-Origin': '*',
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ error: 'Title and content are required' }),
      };
    }

    // Extract version and author from analysis if available
    const version = analysis?.version_info?.latest_version || null;
    const author = analysis?.version_info?.author || 'Uploaded User';

    // Save article to database
    const { data: articleData, error: articleError } = await supabase
      .from('kb_articles')
      .insert([{
        title: title,
        content: content,
        version: version,
        author: author
      }])
      .select();

    if (articleError) throw articleError;

    // Save analysis to database if provided
    if (analysis && articleData && articleData.length > 0) {
      const { error: analysisError } = await supabase
        .from('kb_article_analyses')
        .insert([{
          article_id: articleData[0].id,
          analysis_data: analysis
        }]);

      if (analysisError) {
        console.error('Failed to save analysis:', analysisError);
        // Don't throw error here, article was saved successfully
      }
    }

    return {
      statusCode: 200,
      headers: {
        'Access-Control-Allow-Origin': '*',
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        success: true,
        message: 'Article saved successfully',
        article_id: articleData[0].id
      }),
    };
  } catch (error) {
    console.error('Error saving article:', error);
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