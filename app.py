from flask import Flask, render_template, request
import sqlite3
import os

app = Flask(__name__)

# ---------- DATABASE SETUP ----------
def get_db_connection():
    """Create and return a connection to the SQLite database with timeout."""
    # Timeout ensures the app waits if the database is locked
    conn = sqlite3.connect('users.db', timeout=10)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize the users table with UNIQUE idnumber if it doesn’t exist."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fullname TEXT NOT NULL,
                email TEXT NOT NULL,
                idnumber TEXT UNIQUE NOT NULL,
                role TEXT NOT NULL
            )
        ''')
        conn.commit()

# ---------- ROUTES ----------
@app.route('/')
def index():
    return render_template('reg.html')

@app.route('/submit', methods=['POST'])
def submit():
    fullname = request.form.get('fullname')
    email = request.form.get('email')
    idnumber = request.form.get('idnumber')
    role = request.form.get('role')
    agree = request.form.get('agree')

    if not agree:
        return "<h2>⚠️ Please agree to the Data Privacy Terms and Conditions.</h2>"

    try:
        # Use context manager to ensure connection closes automatically
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO users (fullname, email, idnumber, role) VALUES (?, ?, ?, ?)",
                (fullname, email, idnumber, role)
            )
            conn.commit()

        # Success message
        return "<h2>✅ Registration successful!</h2>"

    except sqlite3.IntegrityError:
        return "<h2>⚠️ This ID number is already registered. Please use another one.</h2>"

    except sqlite3.OperationalError as e:
        return f"<h2>⚠️ Database error: {e}</h2>"

# ---------- RUN APP ----------
if __name__ == '__main__':
    init_db()
    port = int(os.environ.get('PORT', 5000))  # for Render
    app.run(host='0.0.0.0', port=port)
