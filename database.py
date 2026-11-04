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


def add_job_with_skills(title, description, skills):
    conn = sqlite3.connect(DB_NAME)
    try:
        cursor = conn.execute(
            "INSERT INTO jobs (title, description) VALUES (?, ?)",
            (title, description),
        )
        job_id = cursor.lastrowid

        conn.executemany(
            "INSERT INTO skills (job_id, skill) VALUES (?, ?)",
            [(job_id, skill) for skill in skills],
        )

        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

    return job_id


def get_all_jobs():
    conn = sqlite3.connect(DB_NAME)
    rows = conn.execute(
        "SELECT id, title, created_at FROM jobs ORDER BY id"
    ).fetchall()
    conn.close()
    return rows


def count_jobs():
    conn = sqlite3.connect(DB_NAME)
    count = conn.execute("SELECT COUNT(*) FROM jobs").fetchone()[0]
    conn.close()
    return count


def get_top_skills(limit=10):
    conn = sqlite3.connect(DB_NAME)
    rows = conn.execute(
        """
        SELECT skill, COUNT(DISTINCT job_id) AS job_count
        FROM skills
        GROUP BY LOWER(skill)
        ORDER BY job_count DESC, LOWER(skill)
        LIMIT ?
        """,
        (limit,),
    ).fetchall()
    conn.close()
    return rows

def get_skills_for_job(job_id):
    conn = sqlite3.connect(DB_NAME)
    rows = conn.execute(
        "SELECT skill FROM skills WHERE job_id = ? ORDER BY id",
        (job_id,),
        ).fetchall()
    conn.close()
    return [row[0] for row in rows]

def count_unique_skills():
    conn = sqlite3.connect(DB_NAME)
    rows = conn.execute(
        "SELECT COUNT(DISTINCT LOWER(skill)) FROM skills"
    ).fetchone()[0]
    conn.close()
    return rows