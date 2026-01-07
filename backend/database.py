import sqlite3
import os

DB_NAME = "todo.db"

# # For Vercel (Read-only filesystem), use /tmp
# # NOTE: Data will be lost on function restart!
# if os.environ.get('VERCEL'):
#     DB_NAME = "/tmp/todo.db"

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    # Only initialize if the table doesn't exist
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            priority INTEGER NOT NULL,
            is_completed BOOLEAN NOT NULL DEFAULT 0,
            due_date DATE
        )
    ''')
    conn.commit()
    conn.close()
    print("Database initialized.")
