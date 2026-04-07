import sqlite3
from datetime import datetime
import hashlib


class UserManager:
    """
    Manages user accounts in a SQLite database.
    Uses SHA-256 password hashing (MVP; use bcrypt in production).
    """

    def __init__(self, db_path="hardware.db"):
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self._create_table()

    def _create_table(self):
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT DEFAULT 'user',
            created_at TEXT
        )
        """)
        self.conn.commit()

    # ─── Utils ───────────────────────────────────────────────

    def _hash_password(self, password: str) -> str:
        """SHA-256 hash. NOTE: Use bcrypt/argon2 in production."""
        return hashlib.sha256(password.encode()).hexdigest()

    # ─── REGISTER ────────────────────────────────────────────

    def register(self, username: str, password: str, role: str = "user"):
        password_hash = self._hash_password(password)
        try:
            self.cursor.execute(
                "INSERT INTO users (username, password_hash, role, created_at) VALUES (?, ?, ?, ?)",
                (username, password_hash, role, datetime.now().isoformat())
            )
            self.conn.commit()
            print(f"[OK] User '{username}' created with role '{role}'")
            return True
        except sqlite3.IntegrityError:
            print(f"[WARN] Username '{username}' already exists")
            return False

    # ─── LOGIN ───────────────────────────────────────────────

    def login(self, username: str, password: str):
        password_hash = self._hash_password(password)
        self.cursor.execute(
            "SELECT id, username, role FROM users WHERE username = ? AND password_hash = ?",
            (username, password_hash)
        )
        user = self.cursor.fetchone()
        if user:
            return {"id": user[0], "username": user[1], "role": user[2]}
        return None

    # ─── READ ────────────────────────────────────────────────

    def get_user(self, user_id: int):
        self.cursor.execute("SELECT id, username, role, created_at FROM users WHERE id = ?", (user_id,))
        return self.cursor.fetchone()

    def get_all_users(self):
        self.cursor.execute("SELECT id, username, role FROM users")
        return self.cursor.fetchall()

    # ─── DELETE ──────────────────────────────────────────────

    def delete_user(self, user_id: int):
        self.cursor.execute("SELECT 1 FROM users WHERE id = ?", (user_id,))
        if not self.cursor.fetchone():
            print(f"[WARN] No user with ID {user_id}")
            return False
        self.cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
        self.conn.commit()
        print(f"[OK] Deleted user {user_id}")
        return True

    # ─── Connection ──────────────────────────────────────────

    def close(self):
        self.conn.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
