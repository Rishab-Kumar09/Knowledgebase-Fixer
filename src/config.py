import os
from dotenv import load_dotenv
import logging

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    level=os.getenv('LOG_LEVEL', 'INFO'),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Supabase configuration
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError(
        "Missing Supabase credentials. Please set SUPABASE_URL and SUPABASE_KEY in .env file.\n"
        "You can find these in your Supabase project:\n"
        "1. Go to https://supabase.com\n"
        "2. Open your project\n"
        "3. Go to Project Settings -> API\n"
        "4. Copy Project URL and anon public key"
    )

# OpenAI configuration
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

if not OPENAI_API_KEY:
    raise ValueError(
        "Missing OpenAI API key. Please set OPENAI_API_KEY in .env file."
    )

# Flask configuration
FLASK_ENV = os.getenv('FLASK_ENV', 'development')
FLASK_DEBUG = os.getenv('FLASK_DEBUG', '1') == '1' 