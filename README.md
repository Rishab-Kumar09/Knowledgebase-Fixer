# Knowledge Base Analyzer

A tool to analyze knowledge base articles, detect conflicts, and provide improvement recommendations using AI.

## Setup

1. Clone the repository:
```bash
git clone https://github.com/your-username/knowledge-base-analyzer.git
cd knowledge-base-analyzer
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
   - Copy `.env.example` to `.env`:
     ```bash
     cp .env.example .env
     ```
   - Edit `.env` and fill in your credentials:
     - `OPENAI_API_KEY`: Your OpenAI API key
     - `SUPABASE_URL`: Your Supabase project URL
     - `SUPABASE_KEY`: Your Supabase anon/public key

4. Set up Supabase:
   - Create a new project in Supabase
   - Create the following tables:
     ```sql
     -- Articles table
     create table articles (
       id uuid default uuid_generate_v4() primary key,
       title text not null,
       content text not null,
       metadata jsonb default '{}'::jsonb,
       created_at timestamp with time zone default timezone('utc'::text, now())
     );

     -- Article analyses table
     create table article_analyses (
       id uuid default uuid_generate_v4() primary key,
       article_id uuid references articles(id),
       analysis_data jsonb not null,
       created_at timestamp with time zone default timezone('utc'::text, now())
     );
     ```

5. Run the application:
```bash
python src/web/app.py
```

The application will be available at `http://localhost:5000`

## Features

- Upload and analyze knowledge base articles
- Detect conflicts between related articles
- Get AI-powered recommendations for improvements
- SEO optimization suggestions
- Store articles and analyses in Supabase
- File upload support for various formats

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| OPENAI_API_KEY | Your OpenAI API key | Yes |
| SUPABASE_URL | Your Supabase project URL | Yes |
| SUPABASE_KEY | Your Supabase anon/public key | Yes |
| FLASK_ENV | Flask environment (development/production) | No |
| FLASK_DEBUG | Enable Flask debug mode (1/0) | No |
| PORT | Port to run the application (default: 5000) | No |
| DEBUG_MODE | Enable detailed logging (True/False) | No |

## Usage

1. **View Existing Articles**:
   - Open the application in your browser
   - The "Existing Articles" tab shows all articles in your knowledge base
   - Click on any article to analyze it

2. **Add New Article**:
   - Switch to the "New Article" tab
   - Either upload a file or enter content directly
   - Click "Analyze & Save" to process the article

3. **Analysis Results**:
   - View overall quality scores
   - Get technical accuracy assessment
   - See improvement recommendations
   - Review SEO optimization suggestions

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request 