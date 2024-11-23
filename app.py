from flask import Flask, render_template, request
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
    return render_template('index.html')

@app.route('/groups')
def groups():
    conn = get_db_connection()
    cur = conn.cursor()
    
    group_id = request.args.get('group_id')

    if group_id:
        cur.execute('''
        SELECT s.student_id, s.first_name, s.last_name, s.date_of_birth, s.gender, s.address, s.phone, s.email, g.group_name
        FROM Students s
        INNER JOIN Groups g ON s.group_id = g.group_id
        WHERE s.group_id = %s;
    ''', (group_id,))
        show_all_students = False

    else:
        cur.execute('''SELECT s.student_id, s.first_name, s.last_name, s.date_of_birth, s.gender, s.address, s.phone, s.email, g.group_name
        FROM Students s
        INNER JOIN Groups g ON s.group_id = g.group_id
        ORDER BY g.group_name;
        ''')
        show_all_students = True

    students = cur.fetchall()
    
    cur.execute('''
        SELECT g.group_id, g.group_name, c.course_name, COUNT(s.student_id) AS student_count
        FROM Groups g
        INNER JOIN Students s ON g.group_id = s.group_id
        INNER JOIN Courses c ON g.course_id = c.course_id
        GROUP BY g.group_id, g.group_name, c.course_name
        ORDER BY g.group_name;
    ''')
    groups = cur.fetchall()
    cur.close()
    conn.close()
    
    return render_template('groups.html', groups=groups, students=students, show_all_students=show_all_students)

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
        SELECT t.teacher_id, s.subject_name
        FROM Teachers t
        INNER JOIN Schedule sch ON t.teacher_id = sch.teacher_id
        INNER JOIN Subjects s ON sch.subject_id = s.subject_id;
    ''')
    subjects = cur.fetchall()

    # Получение групп, которые ведут преподаватели
    cur.execute('''
        SELECT t.teacher_id, g.group_name
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
        cur.execute('''
            SELECT g.group_name, s.subject_name, sch.day_of_week, sch.start_time, sch.end_time
            FROM Teachers t
            INNER JOIN Schedule sch ON t.teacher_id = sch.teacher_id
            INNER JOIN Groups g ON sch.group_id = g.group_id
            INNER JOIN Subjects s ON sch.subject_id = s.subject_id
            WHERE t.teacher_id = %s;
        ''', (teachers[0][0],))  # По умолчанию показываем расписание первого преподавателя

    schedule = cur.fetchall()

    cur.close()
    conn.close()

    return render_template('teachers.html', teachers=teachers, subjects=subjects, groups=groups, schedule=schedule, selected_teacher_id=teacher_id)

if __name__ == '__main__':
    app.run(debug=True)