from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from datetime import datetime
import sqlite3
import base64
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

DB_NAME = 'visitors.db'

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS visitors (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        mobile TEXT,
        name TEXT,
        post TEXT,
        booth TEXT,
        mandal TEXT,
        reason TEXT,
        photo TEXT,
        in_time TEXT,
        out_time TEXT
    )''')
    conn.commit()
    conn.close()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        data = request.form
        photo_data = data['photo'].split(',')[1] if 'photo' in data and data['photo'] else None
        in_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("INSERT INTO visitors (mobile, name, post, booth, photo, in_time) VALUES (?, ?, ?, ?, ?, ?)",
                  (data['mobile'], data['name'], data['post'], data['booth'], photo_data, in_time))
        conn.commit()
        conn.close()
        return render_template('thanks.html')
    return render_template('index.html')

@app.route('/get_info/<mobile>')
def get_info(mobile):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT name, post, booth FROM visitors WHERE mobile = ? ORDER BY id DESC LIMIT 1", (mobile,))
    row = c.fetchone()
    conn.close()
    if row:
        return jsonify({"name": row[0], "post": row[1], "booth": row[2]})
    return jsonify({})

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        if request.form['username'] == 'admin' and request.form['password'] == 'bjp123':
            session['admin'] = True
            return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if not session.get('admin'):
        return redirect(url_for('admin'))
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT id, mobile, name, post, booth, in_time, out_time FROM visitors ORDER BY id DESC")
    entries = c.fetchall()
    conn.close()
    return render_template('admin.html', entries=entries)

@app.route('/mark_out/<int:visitor_id>')
def mark_out(visitor_id):
    if not session.get('admin'):
        return redirect(url_for('admin'))
    out_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("UPDATE visitors SET out_time = ? WHERE id = ?", (out_time, visitor_id))
    conn.commit()
    conn.close()
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)