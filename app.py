from flask import Flask, render_template, request
import sqlite3

app = Flask(__name__)

# ---------- DATABASE SETUP ----------
def init_db():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    # Create the table with UNIQUE constraint for idnumber
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        fullname TEXT NOT NULL,
                        email TEXT NOT NULL,
                        idnumber TEXT UNIQUE NOT NULL,
                        role TEXT NOT NULL
                    )''')
    conn.commit()
    conn.close()

# ---------- ROUTES ----------
@app.route('/')
def index():
    return render_template('reg.html')

@app.route('/submit', methods=['POST'])
def submit():
    fullname = request.form.get('fullname')
    email = request.form.get('email')
    idnumber = request.form.get('idnumber')  # fixed: match form input name
    role = request.form.get('role')
    agree = request.form.get('agree')

    if not agree:
        return "⚠️ Please agree to the Data Privacy Terms and Conditions."

    try:
        # Save data to SQLite database
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (fullname, email, idnumber, role) VALUES (?, ?, ?, ?)",
                       (fullname, email, idnumber, role))
        conn.commit()
        conn.close()

        return "<h2>Thank you for signing up! You can now use the kiosk.</h2>"

    except sqlite3.IntegrityError:
        # This happens if the idnumber is already registered
        return "<h2>⚠️ This ID number is already registered. Please use another one.</h2>"

# ---------- RUN APP ----------
if __name__ == '__main__':
    init_db()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
