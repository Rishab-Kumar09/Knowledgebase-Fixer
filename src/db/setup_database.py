import os
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables from .env
load_dotenv()

# Get Supabase credentials
supabase_url = os.getenv('SUPABASE_URL')
supabase_key = os.getenv('SUPABASE_KEY')

if not supabase_url or not supabase_key:
    print("Error: SUPABASE_URL and SUPABASE_KEY environment variables are required")
    exit(1)

try:
    # Initialize Supabase client
    supabase: Client = create_client(supabase_url, supabase_key)
    
    # Create the kb_articles table with minimal structure
    create_table_sql = """
    create table if not exists kb_articles (
        id uuid default uuid_generate_v4() primary key,
        path text not null,
        content text not null,
        created_at timestamp with time zone default timezone('utc'::text, now()) not null
    );
    """
    
    # Execute the SQL commands
    result = supabase.table('kb_articles').select("*").execute()
    print("Database setup completed successfully")
    
except Exception as e:
    print(f"Error setting up database: {str(e)}")
    exit(1) 