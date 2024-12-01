from flask import Blueprint, render_template, request, redirect, url_for
from utils import get_db_connection

# Создаем Blueprint для преподавателей
teachers_bp = Blueprint('teachers', __name__)

@teachers_bp.route('/')
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

    # Получение расписания занятий для выбранного преподавателя
    if teacher_id:
        cur.execute('''
            SELECT g.group_name, s.subject_name, sch.day_of_week, sch.start_time, sch.end_time, sch.schedule_id
            FROM Teachers t
            INNER JOIN Schedule sch ON t.teacher_id = sch.teacher_id
            INNER JOIN Groups g ON sch.group_id = g.group_id
            INNER JOIN Subjects s ON sch.subject_id = s.subject_id
            WHERE t.teacher_id = %s;
        ''', (teacher_id,))
        schedule = cur.fetchall()
    else:
        schedule = []

    # Все доступные предметы
    cur.execute('SELECT subject_id, subject_name FROM Subjects;')
    all_subjects = cur.fetchall()

    # Все доступные группы
    cur.execute('SELECT group_id, group_name FROM Groups;')
    all_groups = cur.fetchall()
    cur.close()
    conn.close()

    return render_template('teachers.html', 
                           teachers=teachers, 
                           subjects=subjects, 
                           groups=groups, 
                           schedule=schedule, 
                           selected_teacher_id=teacher_id,
                           all_groups=all_groups,
                           all_subjects=all_subjects)

@teachers_bp.route('/add_schedule', methods=['POST'])
def add_schedule():
    teacher_id = request.form['teacher_id']
    subject_id = request.form['subject_id']
    group_id = request.form['group_id']
    day = request.form['day']
    start_time = request.form['time']
    end_time = request.form['end_time']

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
        INSERT INTO Schedule (teacher_id, subject_id, group_id, day_of_week, start_time, end_time)
        VALUES (%s, %s, %s, %s, %s, %s);
    ''', (teacher_id, subject_id, group_id, day, start_time, end_time))
    conn.commit()
    cur.close()
    conn.close()

    return redirect(url_for('teachers.teachers'))

@teachers_bp.route('/delete_schedule', methods=['POST'])
def delete_schedule():
    schedule_id = request.args.get('schedule_id')
    if not schedule_id:
        return "Не указан ID расписания", 400

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('DELETE FROM Schedule WHERE schedule_id = %s;', (schedule_id,))
    conn.commit()
    cur.close()
    conn.close()

    return redirect(url_for('groups.groups'))