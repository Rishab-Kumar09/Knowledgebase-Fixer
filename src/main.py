#!/usr/bin/env python3

import argparse
import logging
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

from parsers.file_parser import FileParser
from analyzer.content_analyzer import ContentAnalyzer
from reporter.report_generator import ReportGenerator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def parse_arguments():
    parser = argparse.ArgumentParser(
        description='Analyze and improve knowledgebase documentation'
    )
    parser.add_argument(
        '--input-dir',
        type=str,
        required=True,
        help='Directory containing KB articles'
    )
    parser.add_argument(
        '--output-dir',
        type=str,
        required=True,
        help='Directory for generated reports'
    )
    parser.add_argument(
        '--format',
        type=str,
        choices=['html', 'markdown'],
        default='markdown',
        help='Output format for reports'
    )
    return parser.parse_args()

def main():
    # Load environment variables
    load_dotenv()
    
    # Check for OpenAI API key
    if not os.getenv('OPENAI_API_KEY'):
        logger.error('OPENAI_API_KEY environment variable not set')
        sys.exit(1)
    
    # Parse command line arguments
    args = parse_arguments()
    
    try:
        # Initialize components
        file_parser = FileParser()
        content_analyzer = ContentAnalyzer()
        report_generator = ReportGenerator()
        
        # Create output directory if it doesn't exist
        output_dir = Path(args.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Process KB articles
        logger.info(f'Processing articles from {args.input_dir}')
        articles = file_parser.parse_directory(args.input_dir)
        
        # Analyze content
        logger.info('Analyzing content for issues')
        analysis_results = content_analyzer.analyze_articles(articles)
        
        # Generate report
        logger.info(f'Generating {args.format} report')
        report_generator.generate_report(
            analysis_results,
            output_dir,
            format=args.format
        )
        
        logger.info('Analysis complete! Check the output directory for results.')
        
    except Exception as e:
        logger.error(f'An error occurred: {str(e)}')
        sys.exit(1)

if __name__ == '__main__':
    main() 