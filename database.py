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

    conn.execute("""
        CREATE TABLE IF NOT EXISTS my_skills (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            skill TEXT NOT NULL UNIQUE COLLATE NOCASE
        )
    """)

    conn.commit()
    conn.close()


def build_job_filters(title_filter=None, start_date=None, end_date=None):
    conditions = []
    params = []

    if title_filter:
        conditions.append("jobs.title LIKE ?")
        params.append(f"%{title_filter}%")

    if start_date:
        conditions.append("DATE(jobs.created_at, 'localtime') >= ?")
        params.append(start_date)

    if end_date:
        conditions.append("DATE(jobs.created_at, 'localtime') <= ?")
        params.append(end_date)

    if not conditions:
        return "", params

    return "WHERE " + " AND ".join(conditions), params


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


def count_jobs(title_filter=None, start_date=None, end_date=None):
    where, params = build_job_filters(title_filter, start_date, end_date)

    conn = sqlite3.connect(DB_NAME)
    count = conn.execute(
        f"SELECT COUNT(*) FROM jobs {where}",
        params,
    ).fetchone()[0]
    conn.close()
    return count


def get_top_skills(limit=10, title_filter=None, start_date=None, end_date=None):
    where, params = build_job_filters(title_filter, start_date, end_date)

    conn = sqlite3.connect(DB_NAME)
    rows = conn.execute(
        f"""
        SELECT skills.skill, COUNT(DISTINCT skills.job_id) AS job_count
        FROM skills
        JOIN jobs ON jobs.id = skills.job_id
        {where}
        GROUP BY LOWER(skills.skill)
        ORDER BY job_count DESC, LOWER(skills.skill)
        LIMIT ?
        """,
        params + [limit],
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


def count_unique_skills(title_filter=None, start_date=None, end_date=None):
    where, params = build_job_filters(title_filter, start_date, end_date)

    conn = sqlite3.connect(DB_NAME)
    count = conn.execute(
        f"""
        SELECT COUNT(DISTINCT LOWER(skills.skill))
        FROM skills
        JOIN jobs ON jobs.id = skills.job_id
        {where}
        """,
        params,
    ).fetchone()[0]
    conn.close()
    return count


def get_job_date_range():
    conn = sqlite3.connect(DB_NAME)
    first_date, last_date = conn.execute(
        """
        SELECT
            MIN(DATE(created_at, 'localtime')),
            MAX(DATE(created_at, 'localtime'))
        FROM jobs
        """
    ).fetchone()
    conn.close()
    return first_date, last_date

def add_my_skills(skills):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.executemany(
        "INSERT OR IGNORE INTO my_skills (skill) VALUES (?)",
        [(skill,) for skill in skills],
    )
    conn.commit()
    added = cursor.rowcount
    conn.close()
    return added

def remove_my_skills(skills):
    conn = sqlite3.connect(DB_NAME)
    conn.executemany(
        "DELETE FROM my_skills WHERE skill = ?",
        [(skill,) for skill in skills],
    )
    conn.commit()
    conn.close()

def get_my_skills():
    conn = sqlite3.connect(DB_NAME)
    rows = conn.execute(
        "SELECT skill FROM my_skills ORDER BY skill COLLATE NOCASE"
    ).fetchall()
    conn.close()
    return [row[0] for row in rows]