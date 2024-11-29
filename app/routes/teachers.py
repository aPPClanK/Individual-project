from flask import Blueprint, render_template, request
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
            SELECT g.group_name, s.subject_name, sch.day_of_week, sch.start_time, sch.end_time
            FROM Teachers t
            INNER JOIN Schedule sch ON t.teacher_id = sch.teacher_id
            INNER JOIN Groups g ON sch.group_id = g.group_id
            INNER JOIN Subjects s ON sch.subject_id = s.subject_id
            WHERE t.teacher_id = %s;
        ''', (teacher_id,))
        schedule = cur.fetchall()
    else:
        schedule = []

    cur.close()
    conn.close()

    return render_template('teachers.html', 
                           teachers=teachers, 
                           subjects=subjects, 
                           groups=groups, 
                           schedule=schedule, 
                           selected_teacher_id=teacher_id)