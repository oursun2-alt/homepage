# app.py
from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'class_secret_key'

def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, password TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS letters (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, content TEXT, date TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS board (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, username TEXT, content TEXT, date TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    c.execute("SELECT count(*) FROM letters")
    if c.fetchone()[0] == 0:
        c.execute("INSERT INTO letters (title, content, date) VALUES (?, ?, ?)", ('3월 가정통신문', '새 학기가 시작되었습니다. 준비물: 실내화, 알림장', '2026-03-02'))
        c.execute("INSERT INTO letters (title, content, date) VALUES (?, ?, ?)", ('현장체험학습 안내', '다음 주 금요일 에버랜드로 갑니다. 도시락 지참.', '2026-04-10'))
    conn.commit()
    conn.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_pw = generate_password_hash(password)
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_pw))
        conn.commit()
        conn.close()
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = c.fetchone()
        conn.close()
        if user and check_password_hash(user[2], password):
            session['user_id'] = user[0]
            session['username'] = user[1]
            return redirect(url_for('index'))
        else:
            flash('아이디 또는 비밀번호가 틀렸습니다.')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/letters')
def letters():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT * FROM letters ORDER BY id DESC")
    posts = c.fetchall()
    conn.close()
    return render_template('letters.html', posts=posts)

@app.route('/board', methods=['GET', 'POST'])
def board():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        content = request.form['content']
        if content:
            conn = sqlite3.connect('database.db')
            c = conn.cursor()
            c.execute("INSERT INTO board (user_id, username, content) VALUES (?, ?, ?)", (session['user_id'], session['username'], content))
            conn.commit()
            conn.close()
            return redirect(url_for('board'))
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT * FROM board ORDER BY id DESC")
    messages = c.fetchall()
    conn.close()
    return render_template('board.html', messages=messages)

@app.route('/delete_post/<int:post_id>')
def delete_post(post_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("DELETE FROM board WHERE id = ? AND user_id = ?", (post_id, session['user_id']))
    conn.commit()
    conn.close()
    return redirect(url_for('board'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)