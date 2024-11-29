from flask import Blueprint, render_template, request, redirect, url_for
from utils import get_db_connection

news_bp = Blueprint('news', __name__)

@news_bp.route('/')
def index():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
        SELECT news_id, title, content, TO_CHAR(created_at, 'YYYY-MM-DD HH24:MI:SS') AS created_at
        FROM News
        ORDER BY created_at DESC;
    ''')
    news_items = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('index.html', news_items=news_items)

@news_bp.route('/add_news', methods=['POST'])
def add_news():
    title = request.form['title']
    content = request.form['content']
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('INSERT INTO News (title, content) VALUES (%s, %s);', (title, content))
    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for('news.index'))

@news_bp.route('/delete_news/<int:news_id>', methods=['POST'])
def delete_news(news_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('DELETE FROM News WHERE news_id = %s;', (news_id,))
    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for('news.index'))
