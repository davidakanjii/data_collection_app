from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory, flash
import os
import sqlite3
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'xlsx', 'xls', 'csv', 'doc', 'docx'])

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def init_db():
    conn = sqlite3.connect('data/database.db')
    c = conn.cursor()
    # Updated users table to include 'role' with default 'user'
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                 id INTEGER PRIMARY KEY AUTOINCREMENT,
                 username TEXT NOT NULL UNIQUE,
                 password TEXT NOT NULL,
                 role TEXT NOT NULL DEFAULT 'user')''')
    c.execute('''CREATE TABLE IF NOT EXISTS submissions (
                 id INTEGER PRIMARY KEY AUTOINCREMENT,
                 name TEXT,
                 email TEXT,
                 department TEXT,
                 remarks TEXT,
                 filename TEXT,
                 timestamp TEXT)''')
    conn.commit()
    conn.close()

@app.route('/')
def home():
    if 'username' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password'].strip()
        conn = sqlite3.connect('data/database.db')
        c = conn.cursor()
        c.execute("SELECT password, role FROM users WHERE username = ?", (username,))
        user = c.fetchone()
        conn.close()
        if user and check_password_hash(user[0], password):
            session['username'] = username
            session['role'] = user[1]  # Save role in session for access control
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid username or password")
            return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('role', None)
    return redirect(url_for('login'))

@app.route('/form', methods=['GET', 'POST'])
def form():
    if 'username' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        department = request.form['department']
        remarks = request.form['remarks']
        file = request.files['file']
        filename = ""
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        conn = sqlite3.connect('data/database.db')
        c = conn.cursor()
        c.execute("INSERT INTO submissions (name, email, department, remarks, filename, timestamp) VALUES (?, ?, ?, ?, ?, ?)",
                  (name, email, department, remarks, filename, timestamp))
        conn.commit()
        conn.close()
        return redirect(url_for('dashboard'))
    return render_template('form.html')

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))
    conn = sqlite3.connect('data/database.db')
    c = conn.cursor()
    c.execute("SELECT * FROM submissions")
    submissions = c.fetchall()
    conn.close()
    return render_template('dashboard.html', submissions=submissions)

@app.route('/create_user', methods=['POST'])
def create_user_from_dashboard():
    # Only admin users can create new users
    if 'role' not in session or session['role'] != 'admin':
        return redirect(url_for('dashboard'))

    username = request.form['new_username'].strip()
    password = request.form['new_password'].strip()
    role = request.form['new_role'].strip().lower()

    if role not in ['admin', 'user']:
        return "Invalid role selected", 400

    hashed_pw = generate_password_hash(password)

    conn = sqlite3.connect('data/database.db')
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", (username, hashed_pw, role))
        conn.commit()
    except sqlite3.IntegrityError:
        conn.close()
        flash("Username already exists.")
        return redirect(url_for('dashboard'))
    conn.close()

    flash(f"User '{username}' created successfully with role '{role}'.")
    return redirect(url_for('dashboard'))

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
