"""Authentication service: password hashing, JWT tokens, user CRUD."""
import sqlite3
from datetime import datetime, timedelta
from typing import Optional

import bcrypt
from jose import JWTError, jwt

from src.config import settings
from src.db.database import get_connection


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())


def create_token(user_id: int, email: str) -> str:
    payload = {
        "sub": str(user_id),
        "email": email,
        "exp": datetime.utcnow() + timedelta(days=7),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm="HS256")


def verify_token(token: str) -> Optional[dict]:
    try:
        return jwt.decode(token, settings.jwt_secret, algorithms=["HS256"])
    except JWTError:
        return None


def create_user(
    email: str,
    name: str,
    code_id: str,
    password: str,
    software_background: str = "",
    hardware_background: str = "",
) -> dict:
    conn = get_connection()
    try:
        conn.execute(
            """INSERT INTO users
               (email, name, code_id, hashed_password, software_background, hardware_background)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (
                email.lower().strip(),
                name.strip(),
                code_id.strip(),
                hash_password(password),
                software_background.strip(),
                hardware_background.strip(),
            ),
        )
        conn.commit()
        row = conn.execute(
            "SELECT * FROM users WHERE email = ?", (email.lower().strip(),)
        ).fetchone()
        return dict(row)
    except sqlite3.IntegrityError:
        raise ValueError("Email already registered")
    finally:
        conn.close()


def authenticate_user(email: str, password: str) -> Optional[dict]:
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT * FROM users WHERE email = ?", (email.lower().strip(),)
        ).fetchone()
        if not row:
            return None
        if not verify_password(password, row["hashed_password"]):
            return None
        return dict(row)
    finally:
        conn.close()


def get_user_by_id(user_id: int) -> Optional[dict]:
    conn = get_connection()
    try:
        row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()
