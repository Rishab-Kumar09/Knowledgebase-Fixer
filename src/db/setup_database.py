import os
import sys
from pathlib import Path

# Add the parent directory to the Python path
sys.path.append(str(Path(__file__).parent.parent))

from db.supabase_client import SupabaseManager

def setup_database():
    """Set up the database schema in Supabase."""
    try:
        # Initialize Supabase client
        supabase = SupabaseManager()
        
        # Read the schema file
        schema_path = Path(__file__).parent / 'schema.sql'
        with open(schema_path, 'r') as f:
            schema_sql = f.read()
        
        # Split the schema into individual statements
        statements = schema_sql.split(';')
        
        print("Setting up database schema...")
        for statement in statements:
            statement = statement.strip()
            if statement:  # Skip empty statements
                try:
                    # Execute each statement
                    supabase.execute_sql(statement)
                    print("✓ Executed SQL statement successfully")
                except Exception as e:
                    print(f"✗ Error executing statement: {str(e)}")
                    print(f"Statement was: {statement[:100]}...")
        
        print("\nDatabase setup completed!")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    setup_database() 