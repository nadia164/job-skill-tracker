import sqlite3

DB_NAME = "jobs.db"

def create_tables():
    conn = sqlite3.connect(DB_NAME)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS skills (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_id INTEGER NOT NULL,
            skill TEXT NOT NULL,
            FOREIGN KEY (job_id) REFERENCES jobs(id)
        )
    """)

    conn.commit()
    conn.close()

def add_job(title, description):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.execute(
        "INSERT INTO jobs (title, description) VALUES (?, ?)",
        (title, description),
    )

    conn.commit()
    job_id = cursor.lastrowid
    conn.close()
    return job_id

def get_all_jobs():
    conn = sqlite3.connect(DB_NAME)
    rows = conn.execute(
        "SELECT id, title, created_at FROM jobs ORDER by id"
    ).fetchall()

    conn.close()
    return rows