# app.py
from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'class_secret_key'  # 보안을 위한 키 (실제 배포시 복잡하게 변경)

# 데이터베이스 초기화 함수
def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    # 사용자 테이블 생성
    c.execute('''CREATE TABLE IF NOT EXISTS users 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, password TEXT)''')
    # 가정통신문 테이블 생성
    c.execute('''CREATE TABLE IF NOT EXISTS letters 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, content TEXT, date TEXT)''')
    
    # 예시 가정통신문 데이터 넣기 (데이터가 없을 때만)
    c.execute("SELECT count(*) FROM letters")
    if c.fetchone()[0] == 0:
        c.execute("INSERT INTO letters (title, content, date) VALUES (?, ?, ?)", 
                  ('3월 가정통신문', '새 학기가 시작되었습니다. 준비물: 실내화, 알림장', '2026-03-02'))
        c.execute("INSERT INTO letters (title, content, date) VALUES (?, ?, ?)", 
                  ('현장체험학습 안내', '다음 주 금요일 에버랜드로 갑니다. 도시락 지참.', '2026-04-10'))
    
    conn.commit()
    conn.close()

# 메인 페이지
@app.route('/')
def index():
    return render_template('index.html')

# 회원가입
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_pw = generate_password_hash(password) # 비밀번호 암호화

        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_pw))
        conn.commit()
        conn.close()
        return redirect(url_for('login'))
    return render_template('register.html')

# 로그인
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

# 로그아웃
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

# 가정통신문 페이지 (로그인 한 사람만 볼 수 있음)
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

if __name__ == '__main__':
    init_db() # 실행 시 DB 자동 생성
    app.run(debug=True)