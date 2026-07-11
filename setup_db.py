# setup_db.py
import psycopg2
from config import Config

def create_tables():
    conn = psycopg2.connect(
        host=Config.DB_HOST,
        port=Config.DB_PORT,
        database=Config.DB_NAME,
        user=Config.DB_USER,
        password=Config.DB_PASSWORD
    )
    cursor = conn.cursor()
    
    # Users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(255) UNIQUE NOT NULL,
            email VARCHAR(255) UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    
    # Commands history table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS commands_history (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(id),
            command_text VARCHAR(500),
            action_performed VARCHAR(255),
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            result TEXT
        );
    """)
    
    # Memories table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS memories (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(id),
            memory_text TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    
    # Voice settings table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS voice_settings (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(id),
            voice_speed FLOAT DEFAULT 1.0,
            voice_volume FLOAT DEFAULT 1.0,
            wake_word VARCHAR(100) DEFAULT 'hello boss'
        );
    """)
    
    conn.commit()
    cursor.close()
    conn.close()
    print("✅ Database tables created successfully!")

if __name__ == '__main__':
    create_tables()
