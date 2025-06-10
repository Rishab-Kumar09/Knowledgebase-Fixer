const { createClient } = require('@supabase/supabase-js');
const { Configuration, OpenAIApi } = require('openai');

// Initialize Supabase client
const supabaseUrl = process.env.SUPABASE_URL;
const supabaseKey = process.env.SUPABASE_ANON_KEY;
const supabase = createClient(supabaseUrl, supabaseKey);

// Initialize OpenAI
const configuration = new Configuration({
  apiKey: process.env.OPENAI_API_KEY,
});
const openai = new OpenAIApi(configuration);

// CORS headers
const headers = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'Content-Type',
  'Access-Control-Allow-Methods': 'POST, OPTIONS',
};

exports.handler = async (event, context) => {
  // Handle preflight requests
  if (event.httpMethod === 'OPTIONS') {
    return {
      statusCode: 200,
      headers,
      body: '',
    };
  }

  try {
    if (event.httpMethod !== 'POST') {
      throw new Error('Only POST requests are allowed');
    }

    const { content, title, version = 'current', relatedArticles = [] } = JSON.parse(event.body);

    if (!content || !title) {
      throw new Error('Content and title are required');
    }

    // Analyze the article using OpenAI
    const analysisPrompt = `You are an expert technical documentation analyzer. Analyze this knowledge base article and provide a detailed assessment.

Article Title: ${title}
Software Version: ${version}
Content: ${content}

Related Articles for Context: ${relatedArticles.join('\n')}

Provide a comprehensive analysis in the following JSON structure:

{
  "content_analysis": {
    "overall_score": <1-10>,
    "clarity_score": <1-10>,
    "technical_accuracy_score": <1-10>,
    "completeness_score": <1-10>,
    "relevance_score": <1-10>,
    "version_compatibility": {
      "is_current": <boolean>,
      "supported_versions": [<list of versions>],
      "deprecation_status": <string>
    }
  },
  "conflict_analysis": {
    "has_conflicts": <boolean>,
    "conflict_details": [<list of specific conflicts with related articles>],
    "resolution_suggestions": [<list of suggestions to resolve conflicts>]
  },
  "improvement_recommendations": {
    "technical_updates_needed": [<list of technical aspects that need updating>],
    "clarity_improvements": [<list of readability/clarity suggestions>],
    "structure_suggestions": [<list of organizational improvements>],
    "missing_information": [<list of important missing details>]
  },
  "seo_optimization": {
    "keywords": [<list of relevant keywords>],
    "meta_description": <suggested meta description>,
    "title_suggestions": [<list of SEO-friendly title alternatives>]
  },
  "action_items": {
    "priority_level": <"high"|"medium"|"low">,
    "immediate_actions": [<list of urgent updates needed>],
    "long_term_improvements": [<list of non-urgent improvements>]
  },
  "summary": <brief overview of main findings and recommendations>
}

Focus on:
1. Identifying conflicts with other articles
2. Checking version compatibility and deprecation status
3. Technical accuracy and completeness
4. Clarity and structure
5. SEO optimization
6. Actionable recommendations`;

    const completion = await openai.createChatCompletion({
      model: 'gpt-4',
      messages: [
        { role: 'system', content: 'You are an expert technical documentation analyzer.' },
        { role: 'user', content: analysisPrompt }
      ],
      temperature: 0.7,
      max_tokens: 2000
    });

    const analysis = JSON.parse(completion.data.choices[0].message.content);

    // Store the analysis in Supabase
    const { data, error } = await supabase
      .from('kb_analyses')
      .insert([
        {
          title,
          content: content.substring(0, 1000), // Store first 1000 chars as preview
          analysis,
          version,
          timestamp: new Date().toISOString()
        }
      ]);

    if (error) {
      console.error('Supabase error:', error);
    }

    return {
      statusCode: 200,
      headers,
      body: JSON.stringify({ analysis })
    };

  } catch (error) {
    console.error('Error:', error);
    return {
      statusCode: 500,
      headers,
      body: JSON.stringify({ error: error.message })
    };
  }
}; 