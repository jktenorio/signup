from flask import Flask, render_template, request
import sqlite3
import os
import re

app = Flask(__name__)

# ---------- DATABASE SETUP ----------
def get_db_connection():
    """Create and return a connection to the SQLite database with timeout."""
    db_path = os.path.join(os.path.dirname(__file__), 'users.db')
    conn = sqlite3.connect(db_path, timeout=10, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize the users table with UNIQUE idnumber if it doesn’t exist."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            fullname TEXT NOT NULL,
                            email TEXT NOT NULL,
                            idnumber TEXT UNIQUE NOT NULL,
                            role TEXT NOT NULL
                        )''')
        conn.commit()

# ---------- ROUTES ----------
@app.route('/')
def index():
    return render_template('reg.html')

@app.route('/submit', methods=['POST'])
def submit():
    fullname = request.form.get('fullname', '').strip()
    email = request.form.get('email', '').strip()
    idnumber = request.form.get('idnumber', '').strip().replace(' ', '').replace('–', '-')
    role = request.form.get('role', '').strip()
    agree = request.form.get('agree')

    # ✅ Validate agreement
    if not agree:
        return "<h2>⚠️ Please agree to the Data Privacy Terms and Conditions.</h2>"

    # ✅ Validate ID format (####-####)
    if not re.match(r'^\d{4}-\d{4,5}$', idnumber):
        return "<h2>⚠️ Invalid ID number format. Use ####-#### (e.g., 0222-0282).</h2>"

    # ✅ Validate role (must be Student or Faculty)
    if role not in ["Student", "Faculty"]:
        return "<h2>⚠️ Invalid role. Please select Student or Faculty.</h2>"

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO users (fullname, email, idnumber, role) VALUES (?, ?, ?, ?)",
                (fullname, email, idnumber, role)
            )
            conn.commit()

        # ✅ Return success message
        return "<h2>✅ Registration successful! Your information has been saved.</h2>"

    except sqlite3.IntegrityError:
        return "<h2>⚠️ This ID number is already registered. Please use another one.</h2>"

    except sqlite3.OperationalError as e:
        return f"<h2>⚠️ Database error: {e}</h2>"

# ---------- RUN APP ----------
if __name__ == '__main__':
    init_db()
    port = int(os.environ.get('PORT', 5000))  # works locally and on Render
    app.run(host='0.0.0.0', port=port, debug=True)
