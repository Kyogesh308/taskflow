import sqlite3
import contextlib
import os

def get_connection(db_path):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def init_db(db_path):
    os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)
    with contextlib.closing(get_connection(db_path)) as conn:
        with conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS tasks (
                    id          INTEGER PRIMARY KEY AUTOINCREMENT,
                    title       TEXT NOT NULL,
                    description TEXT DEFAULT '',
                    priority    TEXT NOT NULL CHECK (priority IN ('Low','Medium','High')),
                    due_date    TEXT NOT NULL,
                    status      TEXT NOT NULL DEFAULT 'Pending' CHECK (status IN ('Pending','Completed')),
                    created_at  TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
            ''')

def create_task(db_path, title, description, priority, due_date):
    with contextlib.closing(get_connection(db_path)) as conn:
        with conn:
            cursor = conn.execute(
                "INSERT INTO tasks (title, description, priority, due_date, status) VALUES (?, ?, ?, ?, 'Pending')",
                (title, description, priority, due_date)
            )
            return cursor.lastrowid

def get_all_tasks(db_path):
    with contextlib.closing(get_connection(db_path)) as conn:
        cursor = conn.execute(
            "SELECT * FROM tasks ORDER BY CASE status WHEN 'Pending' THEN 1 ELSE 2 END, due_date ASC"
        )
        return [dict(row) for row in cursor.fetchall()]

def get_task(db_path, task_id):
    with contextlib.closing(get_connection(db_path)) as conn:
        cursor = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

def update_task(db_path, task_id, title, description, priority, due_date, status):
    with contextlib.closing(get_connection(db_path)) as conn:
        with conn:
            cursor = conn.execute(
                "UPDATE tasks SET title = ?, description = ?, priority = ?, due_date = ?, status = ? WHERE id = ?",
                (title, description, priority, due_date, status, task_id)
            )
            return cursor.rowcount > 0

def complete_task(db_path, task_id):
    with contextlib.closing(get_connection(db_path)) as conn:
        with conn:
            cursor = conn.execute(
                "UPDATE tasks SET status = 'Completed' WHERE id = ?",
                (task_id,)
            )
            return cursor.rowcount > 0

def delete_task(db_path, task_id):
    with contextlib.closing(get_connection(db_path)) as conn:
        with conn:
            cursor = conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
            return cursor.rowcount > 0
