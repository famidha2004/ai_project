# database.py
import psycopg2
from config import Config

def get_db_connection():
    conn = psycopg2.connect(
        host=Config.DB_HOST,
        port=Config.DB_PORT,
        database=Config.DB_NAME,
        user=Config.DB_USER,
        password=Config.DB_PASSWORD
    )
    return conn

def create_user(username, email):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO users (username, email) VALUES (%s, %s) RETURNING id",
            (username, email)
        )
        user_id = cursor.fetchone()[0]
        conn.commit()
        return user_id
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()

def get_user_memories(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT memory_text, created_at FROM memories WHERE user_id = %s ORDER BY created_at DESC",
        (user_id,)
    )
    memories = cursor.fetchall()
    cursor.close()
    conn.close()
    return memories

def save_memory(user_id, memory_text):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO memories (user_id, memory_text) VALUES (%s, %s)",
            (user_id, memory_text)
        )
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()

def log_command(user_id, command_text, action, result):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO commands_history (user_id, command_text, action_performed, result) VALUES (%s, %s, %s, %s)",
            (user_id, command_text, action, result)
        )
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()
