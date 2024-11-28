from flask import Flask, jsonify, render_template, request, redirect, url_for
from dotenv import load_dotenv
import os
import psycopg2

load_dotenv()

app = Flask(__name__)

DB_HOST = os.getenv('DB_HOST')
DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')

def get_db_connection():
    conn = psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    return conn

@app.route('/')
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

@app.route('/add_news', methods=['POST'])
def add_news():
    title = request.form['title']
    content = request.form['content']
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('INSERT INTO News (title, content) VALUES (%s, %s);', (title, content))
    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for('index'))

@app.route('/delete_news/<int:news_id>', methods=['POST'])
def delete_news(news_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('DELETE FROM News WHERE news_id = %s;', (news_id,))
    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for('index'))

@app.route('/groups')
def groups():
    group_id = request.args.get('group_id')
    student_id = request.args.get('student_id')
    conn = get_db_connection()
    cur = conn.cursor()

    # Получение списка групп
    cur.execute('''
        SELECT g.group_id, g.group_name, c.course_name, COUNT(s.student_id) AS student_count
        FROM Groups g
        LEFT JOIN Students s ON g.group_id = s.group_id
        INNER JOIN Courses c ON g.course_id = c.course_id
        GROUP BY g.group_id, g.group_name, c.course_name
        ORDER BY g.group_name;
    ''')
    groups = cur.fetchall()

    # Получение списка студентов для выбранной группы
    if group_id:
        cur.execute('''
            SELECT s.student_id, s.first_name, s.last_name, s.date_of_birth, s.gender, s.address, s.phone, s.email, g.group_name
            FROM Students s
            INNER JOIN Groups g ON s.group_id = g.group_id
            WHERE s.group_id = %s
            ORDER BY g.group_name, s.first_name;
        ''', (group_id,))
        show_all_students = False
    else:
        cur.execute('''SELECT s.student_id, s.first_name, s.last_name, s.date_of_birth, s.gender, s.address, s.phone, s.email, g.group_name
            FROM Students s
            INNER JOIN Groups g ON s.group_id = g.group_id
            ORDER BY g.group_name, s.first_name;
            ''')
        show_all_students = True

    students = cur.fetchall()

    # Получение данных о посещаемости для конкретного студента
    if student_id:
        cur.execute('''
            SELECT a.date, s.subject_name, a.status
            FROM Attendance a
            INNER JOIN Subjects s ON a.subject_id = s.subject_id
            WHERE a.student_id = %s;
        ''', (student_id,))
        attendance = cur.fetchall()
    else:
        attendance = []

    cur.close()
    conn.close()

    return render_template('groups.html', groups=groups, students=students, show_all_students=show_all_students, attendance=attendance, selected_group_id=group_id, selected_student_id=student_id)

@app.route('/add_group', methods=['POST'])
def add_group():
    group_name = request.form['group_name']
    course_id = request.form['course_id']
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('INSERT INTO Groups (group_name, course_id) VALUES (%s, %s);', (group_name, course_id))
    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for('groups'))

@app.route('/delete_group/<int:group_id>', methods=['POST'])
def delete_group(group_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('DELETE FROM Groups WHERE group_id = %s;', (group_id,))
    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for('groups'))

@app.route('/add_student', methods=['POST'])
def add_student():
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    date_of_birth = request.form['date_of_birth']
    gender = request.form['gender']
    address = request.form['address']
    phone = request.form['phone']
    email = request.form['email']
    group_id = request.form['group_id']
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
        INSERT INTO Students (first_name, last_name, date_of_birth, gender, address, phone, email, group_id)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
    ''', (first_name, last_name, date_of_birth, gender, address, phone, email, group_id))
    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for('groups', group_id=group_id))

@app.route('/delete_student/<int:student_id>', methods=['POST'])
def delete_student(student_id):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        # Начинаем транзакцию
        conn.autocommit = False

        # Удаляем записи из таблицы Attendance
        cur.execute('DELETE FROM Attendance WHERE student_id = %s;', (student_id,))

        # Удаляем запись из таблицы Students
        cur.execute('DELETE FROM Students WHERE student_id = %s;', (student_id,))

        # Подтверждаем транзакцию
        conn.commit()
    except Exception as e:
        # Откатываем транзакцию в случае ошибки
        conn.rollback()
        print(f"Ошибка при удалении студента: {e}")
    finally:
        cur.close()
        conn.close()
    return redirect(url_for('groups'))

@app.route('/get_attendance')
def get_attendance():
    student_id = request.args.get('student_id')
    conn = get_db_connection()
    cur = conn.cursor()

    # Получение данных о посещаемости для студента
    cur.execute('''
        SELECT TO_CHAR(a.date, 'YYYY-MM-DD') AS date, s.subject_name, a.status
        FROM Attendance a
        INNER JOIN Subjects s ON a.subject_id = s.subject_id
        WHERE a.student_id = %s;
    ''', (student_id,))
    attendance = cur.fetchall()

    cur.close()
    conn.close()

    return jsonify(attendance)

@app.route('/schedule')
def schedule():
    conn = get_db_connection()
    cur = conn.cursor()

    # Получение списка групп
    cur.execute('SELECT group_id, group_name FROM Groups;')
    groups = cur.fetchall()
    
    # Получение выбранной группы из параметров запроса
    selected_group = request.args.get('group')

    # Фильтрация расписания по выбранной группе
    if selected_group:
        cur.execute('''
            SELECT s.group_id, g.group_name, s.subject_id, sub.subject_name, s.day_of_week, s.start_time, s.end_time
            FROM Schedule s
            JOIN Groups g ON s.group_id = g.group_id
            JOIN Subjects sub ON s.subject_id = sub.subject_id
            WHERE s.group_id = %s
            ORDER BY s.start_time, s.day_of_week;
        ''', (selected_group,))
    else:
        cur.execute('''
            SELECT s.group_id, g.group_name, s.subject_id, sub.subject_name, s.day_of_week, s.start_time, s.end_time
            FROM Schedule s
            JOIN Groups g ON s.group_id = g.group_id
            JOIN Subjects sub ON s.subject_id = sub.subject_id
            ORDER BY s.start_time, s.day_of_week;
        ''')

    schedule = cur.fetchall()
    cur.close()
    conn.close()

    return render_template('schedule.html', schedule=schedule, groups=groups, selected_group=selected_group)

@app.route('/teachers')
def teachers():
    teacher_id = request.args.get('teacher_id')
    conn = get_db_connection()
    cur = conn.cursor()

    # Получение списка преподавателей
    cur.execute('''
        SELECT t.teacher_id, t.first_name, t.last_name, t.date_of_birth, t.gender, t.address, t.phone, t.email
        FROM Teachers t;
    ''')
    teachers = cur.fetchall()

    # Получение предметов, которые преподают преподаватели
    cur.execute('''
        SELECT DISTINCT t.teacher_id, s.subject_name
        FROM Teachers t
        INNER JOIN Schedule sch ON t.teacher_id = sch.teacher_id
        INNER JOIN Subjects s ON sch.subject_id = s.subject_id;
    ''')
    subjects = cur.fetchall()

    # Получение групп, которые ведут преподаватели
    cur.execute('''
        SELECT DISTINCT t.teacher_id, g.group_name
        FROM Teachers t
        INNER JOIN Schedule sch ON t.teacher_id = sch.teacher_id
        INNER JOIN Groups g ON sch.group_id = g.group_id;
    ''')
    groups = cur.fetchall()

    # Получение расписания занятий для преподавателя
    if teacher_id:
        cur.execute('''
            SELECT g.group_name, s.subject_name, sch.day_of_week, sch.start_time, sch.end_time
            FROM Teachers t
            INNER JOIN Schedule sch ON t.teacher_id = sch.teacher_id
            INNER JOIN Groups g ON sch.group_id = g.group_id
            INNER JOIN Subjects s ON sch.subject_id = s.subject_id
            WHERE t.teacher_id = %s;
        ''', (teacher_id,))
    else:
        schedule = []

    schedule = cur.fetchall()

    cur.close()
    conn.close()

    return render_template('teachers.html', teachers=teachers, subjects=subjects, groups=groups, schedule=schedule, selected_teacher_id=teacher_id)

if __name__ == '__main__':
    app.run(debug=True)