# Knowledgebase Fixer

An AI-powered tool to analyze and improve internal knowledgebase documentation by identifying outdated, conflicting, or irrelevant articles.

## Features

- 📚 Crawl KB articles (markdown, HTML, plain text)
- 🔍 Detect outdated versions and conflicting information
- ⚖️ Score articles for correctness and relevance
- ✍️ AI-powered edit suggestions using GPT
- 📊 Generate comprehensive analysis reports

## Tech Stack

- Python 3.9+
- OpenAI GPT-4
- Beautiful Soup 4 (HTML parsing)
- Markdown Parser
- Jinja2 (Report templating)

## Project Structure

```
knowledgebase-fixer/
├── src/
│   ├── parsers/         # File parsing modules
│   ├── analyzer/        # AI analysis logic
│   ├── reporter/        # Report generation
│   └── utils/           # Helper functions
├── tests/               # Test cases
├── examples/            # Example KB articles
├── reports/             # Generated reports
└── config/             # Configuration files
```

## Setup

1. Clone the repository:
```bash
git clone https://github.com/Rishab-Kumar09/Knowledgebase-Fixer.git
cd Knowledgebase-Fixer
```

2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your OpenAI API key
```

## Usage

Basic usage:
```bash
python src/main.py --input-dir /path/to/kb/articles --output-dir /path/to/reports
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details. 