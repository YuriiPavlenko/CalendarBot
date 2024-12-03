import sqlite3

def get_db_connection():
    """Get a connection to the SQLite database."""
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

def initialize_db():
    """Initialize the database with the necessary tables."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            language TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close() 