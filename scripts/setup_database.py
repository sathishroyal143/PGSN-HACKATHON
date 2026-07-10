"""
Database setup script for CareBridge-AI.
Creates PostgreSQL database and user if they don't exist.
"""

import os
import sys
import psycopg2
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables
from decouple import config


def create_database():
    """Create PostgreSQL database and user"""
    
    # Database configuration
    db_name = config('DB_NAME', default='carebridge_db')
    db_user = config('DB_USER', default='postgres')
    db_password = config('DB_PASSWORD', default='postgres')
    db_host = config('DB_HOST', default='localhost')
    db_port = config('DB_PORT', default='5432')
    
    print(f"Setting up database: {db_name}")
    print(f"Host: {db_host}:{db_port}")
    print(f"User: {db_user}")
    
    try:
        # Connect to PostgreSQL server (default postgres database)
        conn = psycopg2.connect(
            host=db_host,
            port=db_port,
            user='postgres',  # Default postgres superuser
            password=db_password,
            database='postgres'
        )
        
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Check if database exists
        cursor.execute(
            "SELECT 1 FROM pg_database WHERE datname = %s",
            (db_name,)
        )
        
        if cursor.fetchone():
            print(f"[OK] Database '{db_name}' already exists")
        else:
            # Create database
            cursor.execute(
                sql.SQL("CREATE DATABASE {}").format(
                    sql.Identifier(db_name)
                )
            )
            print(f"[OK] Database '{db_name}' created successfully")
        
        # Set database configuration
        cursor.execute(
            sql.SQL("ALTER DATABASE {} SET timezone TO 'Asia/Kolkata'").format(
                sql.Identifier(db_name)
            )
        )
        print(f"[OK] Database timezone set to Asia/Kolkata")
        
        cursor.close()
        conn.close()
        
        print("\n[OK] Database setup completed successfully!")
        return True
        
    except psycopg2.Error as e:
        print(f"\nX Database setup failed: {e}")
        return False
    except Exception as e:
        print(f"\nX Unexpected error: {e}")
        return False


def test_connection():
    """Test database connection"""
    
    db_name = config('DB_NAME', default='carebridge_db')
    db_user = config('DB_USER', default='postgres')
    db_password = config('DB_PASSWORD', default='postgres')
    db_host = config('DB_HOST', default='localhost')
    db_port = config('DB_PORT', default='5432')
    
    try:
        print("\nTesting database connection...")
        
        conn = psycopg2.connect(
            host=db_host,
            port=db_port,
            user=db_user,
            password=db_password,
            database=db_name
        )
        
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        
        print(f"[OK] Connection successful!")
        print(f"[OK] PostgreSQL version: {version[0]}")
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"X Connection failed: {e}")
        return False


if __name__ == '__main__':
    print("=" * 60)
    print("CareBridge-AI Database Setup")
    print("=" * 60)
    
    # Create database
    if create_database():
        # Test connection
        test_connection()
        
        print("\n" + "=" * 60)
        print("Next steps:")
        print("1. Run: python manage.py makemigrations")
        print("2. Run: python manage.py migrate")
        print("3. Run: python manage.py createsuperuser")
        print("=" * 60)
    else:
        print("\nPlease fix the errors and try again.")
        sys.exit(1)
