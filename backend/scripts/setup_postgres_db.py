"""Script to check, create, and initialize PostgreSQL database for Legal Metrology Scanner."""
import sys
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

POSTGRES_USER = "postgres"
POSTGRES_PASS = "postgres"
POSTGRES_HOST = "localhost"
POSTGRES_PORT = "5432"
DB_NAME = "legal_metrology_db"

def setup_postgres():
    print(f"Connecting to PostgreSQL server at {POSTGRES_HOST}:{POSTGRES_PORT} as {POSTGRES_USER}...")
    try:
        conn = psycopg2.connect(
            user=POSTGRES_USER,
            password=POSTGRES_PASS,
            host=POSTGRES_HOST,
            port=POSTGRES_PORT,
            dbname="postgres"
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Check if database exists
        cursor.execute(f"SELECT 1 FROM pg_catalog.pg_database WHERE datname = '{DB_NAME}';")
        exists = cursor.fetchone()
        
        if not exists:
            print(f"Creating database '{DB_NAME}'...")
            cursor.execute(f"CREATE DATABASE {DB_NAME};")
            print(f"Database '{DB_NAME}' created successfully.")
        else:
            print(f"Database '{DB_NAME}' already exists.")
            
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"Note: PostgreSQL connection with default credentials: {e}")
        return False

if __name__ == "__main__":
    setup_postgres()
