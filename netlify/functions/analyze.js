const { Configuration, OpenAIApi } = require('openai');
const { createClient } = require('@supabase/supabase-js');

const supabase = createClient(
  process.env.SUPABASE_URL,
  process.env.SUPABASE_KEY
);

const openai = new OpenAIApi(new Configuration({
  apiKey: process.env.OPENAI_API_KEY
}));

exports.handler = async (event, context) => {
  const headers = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Access-Control-Allow-Methods': 'POST, OPTIONS'
  };

  // Handle preflight request
  if (event.httpMethod === 'OPTIONS') {
    return {
      statusCode: 200,
      headers,
      body: ''
    };
  }

  try {
    let articleId, content;
    
    if (event.path.includes('/analyze/')) {
      // Analyzing existing article
      articleId = event.path.split('/').pop();
      const { data: article, error } = await supabase
        .from('articles')
        .select('content')
        .eq('id', articleId)
        .single();

      if (error) throw error;
      content = article.content;
    } else {
      // Analyzing new content
      const body = JSON.parse(event.body);
      content = body.content;
    }

    const prompt = `Please analyze this knowledge base article and provide:
    1. Overall quality score (0-100)
    2. Clarity score (0-100)
    3. Technical accuracy score (0-100)
    4. Completeness score (0-100)
    5. List of recommendations for improvement
    6. SEO optimization suggestions

    Article content:
    ${content}`;

    const response = await openai.createChatCompletion({
      model: 'gpt-4',
      messages: [{ role: 'user', content: prompt }]
    });

    const analysis = response.data.choices[0].message.content;
    
    // Store analysis if it's for an existing article
    if (articleId) {
      await supabase
        .from('article_analyses')
        .insert([{
          article_id: articleId,
          analysis_data: { raw_analysis: analysis }
        }]);
    }

    return {
      statusCode: 200,
      headers: {
        'Content-Type': 'application/json',
        ...headers
      },
      body: JSON.stringify({ analysis })
    };

  } catch (error) {
    console.error('Error:', error);
    return {
      statusCode: 500,
      headers: {
        'Content-Type': 'application/json',
        ...headers
      },
      body: JSON.stringify({ error: 'Internal server error' })
    };
  }
}; 