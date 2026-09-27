import re

from flask import Blueprint, jsonify, request, session
from werkzeug.security import check_password_hash, generate_password_hash

from db import get_connection, put_connection

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


@auth_bp.post("/signup")
def signup():
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    if not EMAIL_RE.match(email):
        return jsonify({"error": "A valid email is required."}), 400
    if len(password) < 8:
        return jsonify({"error": "Password must be at least 8 characters."}), 400

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM users WHERE email = %s", (email,))
            if cur.fetchone():
                return jsonify({"error": "An account with that email already exists."}), 409

            password_hash = generate_password_hash(password)
            cur.execute(
                "INSERT INTO users (email, password_hash) VALUES (%s, %s) RETURNING id, email",
                (email, password_hash),
            )
            user_id, user_email = cur.fetchone()
            conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        put_connection(conn)

    session["user_id"] = user_id
    session["user_email"] = user_email
    return jsonify({"user": {"id": user_id, "email": user_email}}), 201


@auth_bp.post("/login")
def login():
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    if not email or not password:
        return jsonify({"error": "Email and password are required."}), 400

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, email, password_hash FROM users WHERE email = %s", (email,)
            )
            row = cur.fetchone()
    finally:
        put_connection(conn)

    # Same error for "no such user" and "wrong password" so we don't leak which emails exist.
    if not row or not check_password_hash(row[2], password):
        return jsonify({"error": "Invalid email or password."}), 401

    user_id, user_email, _ = row
    session["user_id"] = user_id
    session["user_email"] = user_email
    return jsonify({"user": {"id": user_id, "email": user_email}})


@auth_bp.post("/logout")
def logout():
    session.clear()
    return jsonify({"ok": True})


@auth_bp.get("/me")
def me():
    if "user_id" not in session:
        return jsonify({"user": None})
    return jsonify({"user": {"id": session["user_id"], "email": session["user_email"]}})
