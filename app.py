from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import random
from datetime import datetime, timedelta

app = Flask(__name__)
DATABASE = 'diary.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# データベースの初期化
def init_db():
    with get_db_connection() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS entries (
                id INTEGER PRIMARY KEY,
                date TEXT NOT NULL,
                when_time TEXT,
                where_loc TEXT,
                who TEXT,
                what TEXT,
                why TEXT,
                how TEXT,
                location_tag TEXT,
                emotion_tag TEXT,
                keywords TEXT
            )
        ''')
        conn.commit()

# アプリケーション起動時にデータベースを初期化
with app.app_context():
    init_db()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    # フォームからデータを取得し、データベースに保存
    data = request.form
    when_time = data.get('when')
    where_loc = data.get('where')
    who = data.get('who')
    what = data.get('what')
    why = data.get('why')
    how = data.get('how')
    location_tag = data.get('location_tag')
    emotion_tag = data.get('emotion_tag')
    keywords = data.get('keywords')
    current_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    with get_db_connection() as conn:
        conn.execute('''
            INSERT INTO entries (date, when_time, where_loc, who, what, why, how, location_tag, emotion_tag, keywords)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (current_date, when_time, where_loc, who, what, why, how, location_tag, emotion_tag, keywords))
        conn.commit()

    return redirect(url_for('index'))

@app.route('/quiz')
def quiz():
    # ランダムに日記の質問を生成
    with get_db_connection() as conn:
        entries = conn.execute('SELECT * FROM entries ORDER BY RANDOM() LIMIT 1').fetchone()
    
    if entries:
        questions = [
            f"{entries['date']}の出来事は、いつ起きましたか？",
            f"{entries['date']}の出来事は、どこで起きましたか？",
            f"{entries['date']}の出来事には、誰が登場しましたか？",
            f"{entries['date']}の出来事は、何でしたか？"
        ]
        question = random.choice(questions)
        return f"<h1>今日のクイズ</h1><p>{question}</p><p>答え: {entries['what']}</p>"
    
    return "<h1>クイズ</h1><p>まだ日記がありません。</p>"

@app.route('/review')
def review():
    # すべての日記を表示
    with get_db_connection() as conn:
        entries = conn.execute('SELECT * FROM entries ORDER BY date DESC').fetchall()
    return render_template('review.html', entries=entries)

if __name__ == '__main__':
    app.run(debug=True)