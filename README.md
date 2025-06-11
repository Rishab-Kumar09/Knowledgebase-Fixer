# 📚 Knowledge Base Analyzer

A comprehensive AI-powered Knowledge Base analysis tool that helps organizations maintain high-quality, secure, and up-to-date documentation. Built with modern web technologies and deployed on Netlify with Supabase backend.

![Knowledge Base Analyzer](https://img.shields.io/badge/Status-Production%20Ready-brightgreen)
![Version](https://img.shields.io/badge/Version-2.0-blue)
![License](https://img.shields.io/badge/License-MIT-green)

## 🚀 Live Demo

**Deployed Application:** [knowledgebase-fixer.netlify.app](https://knowledgebase-fixer.netlify.app)

## 🎯 Overview

The Knowledge Base Analyzer is an enterprise-grade solution designed to:
- **Analyze individual articles** for security vulnerabilities and quality issues
- **Detect conflicts** between different articles in your knowledge base
- **Flag deprecated content** that needs immediate attention
- **Score article relevance** with time-based decay analysis
- **Provide executive dashboards** with actionable insights
- **Prioritize actions** by urgency and impact

## ✨ Features

### Phase 1: Individual Article Analysis ✅
- **Security Issue Detection**: Identifies common security vulnerabilities and bad practices
- **Content Quality Scoring**: Evaluates freshness, technical accuracy, and clarity
- **Version Tracking**: Extracts and tracks version information from articles
- **Real-time Analysis**: Instant feedback on uploaded articles
- **Database Integration**: Save analyzed articles for future reference

### Phase 2: Cross-Article Conflict Detection ✅
- **Conflict Analysis**: Detects contradictory advice between articles
- **Deprecated Technology Scanner**: Flags outdated practices (MD5, SHA1, HTTP, Flash, etc.)
- **Relevance Scoring**: Time-based freshness calculation with decay
- **Health Dashboard**: Executive-level overview with visual metrics
- **Action Prioritization**: Categorizes issues by urgency (HIGH/MEDIUM/LOW)

## 🏗️ Architecture

```
Frontend (HTML/CSS/JS)
├── Upload Interface
├── Existing Articles Analysis
├── Phase 2 Conflict Detection
└── Results Dashboard

Backend (Netlify Functions)
├── analyze.js - Individual article analysis
├── analyze-all.js - Bulk article processing
├── detect-conflicts.js - Cross-article conflict detection
├── save-article.js - Database operations
└── package.json - Dependencies

Database (Supabase PostgreSQL)
├── kb_articles - Store articles and metadata
├── kb_article_analyses - Store analysis results
├── Indexes for performance
└── Auto-update triggers
```

## 🛠️ Technology Stack

### Frontend
- **HTML5** - Semantic markup and structure
- **CSS3** - Responsive design with modern styling
- **Vanilla JavaScript** - No framework dependencies for maximum performance

### Backend
- **Node.js** - Runtime environment
- **Netlify Functions** - Serverless compute
- **OpenAI GPT** - AI-powered content analysis
- **Supabase** - PostgreSQL database with real-time features

### Infrastructure
- **Netlify** - Static site hosting and serverless functions
- **GitHub** - Version control and CI/CD
- **Supabase** - Database hosting and management

## 📦 Installation & Setup

### Prerequisites
- Node.js 18+ and npm
- Supabase account
- OpenAI API key
- Netlify account (for deployment)

### 1. Clone the Repository
```bash
git clone https://github.com/Rishab-Kumar09/Knowledgebase-Fixer.git
cd Knowledgebase-Fixer
```

### 2. Install Dependencies
```bash
# Install root dependencies
npm install

# Install Netlify Functions dependencies
cd netlify/functions
npm install
cd ../..
```

### 3. Environment Configuration
Create a `.env` file in the root directory:
```env
# OpenAI Configuration
OPENAI_API_KEY=sk-your-openai-api-key-here

# Supabase Configuration
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_ANON_KEY=your-supabase-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-supabase-service-role-key
```

### 4. Database Setup
Execute the following SQL in your Supabase SQL Editor:

```sql
-- Create articles table
CREATE TABLE kb_articles (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    version VARCHAR(50),
    author VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create analyses table
CREATE TABLE kb_article_analyses (
    id SERIAL PRIMARY KEY,
    article_id INTEGER REFERENCES kb_articles(id) ON DELETE CASCADE,
    analysis_data JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for performance
CREATE INDEX idx_kb_articles_title ON kb_articles(title);
CREATE INDEX idx_kb_articles_created_at ON kb_articles(created_at);
CREATE INDEX idx_kb_article_analyses_article_id ON kb_article_analyses(article_id);

-- Auto-update trigger for articles
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_kb_articles_updated_at BEFORE UPDATE
    ON kb_articles FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
```

### 5. Local Development
```bash
# Install Netlify CLI globally
npm install -g netlify-cli

# Start local development server
netlify dev
```

Visit `http://localhost:8888` to access the application.

### 6. Deploy to Netlify

#### Option A: Connect GitHub Repository
1. Fork this repository to your GitHub account
2. Connect your Netlify account to GitHub
3. Import the repository in Netlify
4. Add environment variables in Netlify dashboard
5. Deploy!

#### Option B: Manual Deployment
```bash
# Build and deploy
netlify deploy --prod
```

## 📋 Usage Guide

### Upload Articles Tab
1. **Upload Files**: Drag and drop text files or click to select
2. **Real-time Analysis**: Get instant security and quality feedback
3. **Save to Database**: Store analyzed articles for future reference
4. **View Results**: See detailed analysis with scores and recommendations

### Existing Articles Tab
1. **Analyze Database**: Process all articles stored in your database
2. **Bulk Operations**: Efficient analysis of large article collections
3. **Version Tracking**: See version information and metadata
4. **Issue Detection**: Identify security vulnerabilities across all content

### Phase 2: Conflict Detection Tab
1. **Run Complete Analysis**: Click the analysis button
2. **Health Dashboard**: View overall knowledge base health metrics
3. **Conflict Matrix**: See articles that contradict each other
4. **Deprecated Content**: Review outdated technologies and practices
5. **Action Items**: Get prioritized recommendations for improvements

## 🔍 Analysis Capabilities

### Security Issues Detected
- **API Key Storage**: Plain text API keys in code
- **Password Hashing**: Weak hashing algorithms (MD5, SHA1)
- **Database Security**: Hardcoded credentials and insecure connections
- **File Upload Security**: Unvalidated file uploads
- **Cookie Security**: Missing security flags
- **SQL Injection**: Vulnerable query patterns
- **Cross-Site Scripting (XSS)**: Unsafe HTML handling
- **HTTPS Usage**: HTTP connections in production

### Content Quality Metrics
- **Freshness Score**: Based on creation/update dates and version information
- **Technical Accuracy**: Evaluation of technical recommendations
- **Clarity Score**: Assessment of writing quality and structure
- **Completeness**: Coverage of important topics and edge cases

### Conflict Detection Categories
- **Authentication Methods**: Conflicting password policies
- **Authorization Practices**: Inconsistent access control recommendations
- **Data Storage**: Contradictory database security advice
- **API Security**: Different API protection strategies
- **File Handling**: Conflicting file upload policies
- **Network Security**: Mixed HTTP/HTTPS recommendations
- **Backup Strategies**: Inconsistent backup and recovery advice

## 📊 Sample Analysis Results

### Health Dashboard Metrics
```
Overall Health Score: 73%
├── Total Articles: 12
├── Conflicts Found: 2
├── Deprecated Articles: 1
└── Articles Needing Review: 3

Action Required:
├── 1 item needs immediate attention
└── 3 items need review
```

### Conflict Example
```
HIGH SEVERITY CONFLICT
Category: PASSWORD_SECURITY
Articles: "Legacy Security Guide" vs "Modern Security Practices"
Issue: Contradictory password hashing recommendations
Recommendation: Update legacy article to use bcrypt instead of MD5
```

### Deprecated Content Example
```
HIGH PRIORITY DEPRECATED CONTENT
Article: "Legacy Security Practices Guide"
Features:
├── MD5 (Deprecated: 2012) - Cryptographically broken
├── HTTP (Deprecated: 2015) - Use HTTPS for all connections
└── Plain text storage (Deprecated: Always) - Use environment variables
```

## 🔧 Configuration

### OpenAI Settings
The system uses GPT-3.5-turbo for analysis. You can modify the prompts in:
- `netlify/functions/analyze.js` - Individual analysis
- `netlify/functions/detect-conflicts.js` - Conflict detection

### Database Schema
Extend the database schema by adding fields to:
- `kb_articles` table for additional metadata
- `kb_article_analyses` table for extended analysis data

### Analysis Rules
Customize detection rules in:
- Security patterns in analysis functions
- Deprecated technology lists
- Conflict detection categories

## 🚀 Deployment

### Netlify Configuration (`netlify.toml`)
```toml
[build]
  command = "npm install && pip install -r requirements.txt"
  publish = "public"
  functions = "netlify/functions"

[build.environment]
  NODE_VERSION = "18"

[[plugins]]
  package = "@netlify/plugin-functions-install-core"
```

### Environment Variables Required
- `OPENAI_API_KEY`
- `SUPABASE_URL`
- `SUPABASE_ANON_KEY`
- `SUPABASE_SERVICE_ROLE_KEY`

## 🤝 Contributing

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Commit your changes**: `git commit -m 'Add amazing feature'`
4. **Push to the branch**: `git push origin feature/amazing-feature`
5. **Open a Pull Request**

### Development Guidelines
- Follow existing code style and conventions
- Add tests for new features
- Update documentation for API changes
- Ensure all checks pass before submitting PR

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support & Troubleshooting

### Common Issues

#### Files Not Loading (404 Errors)
- Ensure CSS and JS files are in the `public/` directory
- Check Netlify build logs for file copying errors

#### Database Connection Issues
- Verify Supabase credentials in environment variables
- Check database table exists and has correct schema
- Ensure Row Level Security (RLS) is properly configured

#### OpenAI API Errors
- Verify API key is valid and has sufficient credits
- Check rate limits if getting 429 errors
- Monitor token usage for large articles

#### Netlify Function Timeouts
- Functions have a 10-second timeout limit
- Consider breaking large analyses into smaller chunks
- Optimize database queries for better performance

### Debug Mode
Add `console.log` statements in the browser console to trace:
- `conflictDetector.detectConflicts()` - Phase 2 analysis
- Network tab for API call responses
- Application tab for localStorage data

### Performance Optimization
- **Database**: Add indexes for frequently queried columns
- **API**: Implement caching for repeated analyses
- **Frontend**: Lazy load analysis results for large datasets

## 📞 Contact

- **GitHub**: [@Rishab-Kumar09](https://github.com/Rishab-Kumar09)
- **Project Repository**: [Knowledgebase-Fixer](https://github.com/Rishab-Kumar09/Knowledgebase-Fixer)
- **Live Application**: [knowledgebase-fixer.netlify.app](https://knowledgebase-fixer.netlify.app)

---

**Built with ❤️ for better knowledge management** 