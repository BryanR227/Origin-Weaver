# Origin Weaver — Login/Signup with Tiger

This replaces the earlier Node/`auth.js` approach — since your backend is
Flask, auth is now a Flask blueprint using session cookies (no separate
`auth.js` file needed; `chat.js` handles it directly, same-origin, no CORS).

**Delete or ignore the standalone `auth.js` file from earlier — it's for a
Node backend and doesn't apply here.**

## Files in this drop, mapped to your repo

- `database/schema.sql` → add to your existing `database/` folder
- `gemini/db.py` → new file, next to `gemini/app.py`
- `gemini/auth.py` → new file, next to `gemini/app.py`
- `gemini/app.py` → replaces your existing one (added: `from auth import auth_bp`,
  `app.secret_key`, `app.register_blueprint(auth_bp)` — nothing else changed)
- `frontend/chat.js` → replaces your existing one (only the auth-related
  code changed: `setAuthMode`, `accountButton` click handler, and the
  `authForm` submit handler now call the real API instead of showing
  "Authentication is not connected yet")

## Setup

1. **Install the Postgres driver**
   ```
   pip install psycopg2-binary
   ```
   Add it to your `requirements.txt` too.

2. **Create the `users` table in Tiger**
   ```
   psql "$DATABASE_URL" -f database/schema.sql
   ```
   (Or paste `schema.sql` into any Postgres client connected to your Tiger service.)

3. **Add to your `.env`**
   ```
   DATABASE_URL=postgresql://tsdbadmin:yourpassword@your-service.tsdb.cloud.timescale.com:5432/tsdb?sslmode=require
   SECRET_KEY=replace-with-a-long-random-string
   ```
   `DATABASE_URL` is your Tiger Cloud connection string (from the Tiger console).
   `SECRET_KEY` is used by Flask to sign the session cookie — any long random string.

4. **Run the app as usual**
   ```
   python app.py
   ```
   (from inside `gemini/`, same as before)

## How it works

- `POST /api/auth/signup` — `{ email, password }` → creates the user (password hashed with Werkzeug's `generate_password_hash`), logs them in, sets a session cookie
- `POST /api/auth/login` — `{ email, password }` → verifies and logs in
- `POST /api/auth/logout` — clears the session
- `GET /api/auth/me` — `{ user: {...} }` or `{ user: null }`, used on page load to check if someone's already signed in

Since Flask serves the frontend itself, everything is same-origin — the browser handles the session cookie automatically, no tokens to manage in JavaScript.

## Notes on Tiger

- Tiger Cloud requires SSL; make sure `?sslmode=require` is in your `DATABASE_URL`.
- The `users` table is a plain Postgres table — no Timescale-specific features needed, since accounts aren't time-series data.
