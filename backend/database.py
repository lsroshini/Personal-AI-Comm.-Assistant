import sqlite3
from config import DB_FILE

# Connect to SQLite database and create tables
with sqlite3.connect(DB_FILE) as conn:
    cursor = conn.cursor()

    # Table for storing tasks extracted from emails
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email_id TEXT UNIQUE,
        sender TEXT,
        due_date TEXT,
        days_left INTEGER,
        priority_score INTEGER
    );
    """)

    # Table for storing summarized emails
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS email_summaries (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email_id TEXT UNIQUE,
        summary TEXT
    );
    """)

    conn.commit()

def save_tasks_to_db(tasks):
    """Stores task priority details in the database."""
    if not tasks:
        print("⚠️ No tasks to save.")
        return

    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        for task in tasks:
            if not all(key in task for key in ["email_id", "sender", "due_date", "days_left", "priority_score"]):
                print(f"⚠️ Skipping task due to missing fields: {task}")
                continue

            cursor.execute("""
                INSERT OR IGNORE INTO tasks (email_id, sender, due_date, days_left, priority_score)
                VALUES (?, ?, ?, ?, ?)
            """, (task["email_id"], task["sender"], task["due_date"], task["days_left"], task["priority_score"]))

        conn.commit()
        print("✅ Tasks saved successfully.")

def save_summaries_to_db(summaries):
    """Stores email summaries in the database."""
    if not summaries:
        print("⚠️ No summaries to save.")
        return

    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        for summary in summaries:
            if not all(key in summary for key in ["email_id", "summary"]):
                print(f"⚠️ Skipping summary due to missing fields: {summary}")
                continue

            # Ensure summary is a string
            summary_text = summary["summary"]
            if isinstance(summary_text, list):  
                summary_text = " ".join(summary_text)  # Convert list to string

            cursor.execute("""
                INSERT OR REPLACE INTO email_summaries (email_id, summary)
                VALUES (?, ?)
            """, (summary["email_id"], summary_text))


        conn.commit()
        print("✅ Summaries saved successfully.")
