from flask import Blueprint, render_template, request
from utils import get_db_connection

# Создаём Blueprint для расписания
schedule_bp = Blueprint('schedule', __name__)

@schedule_bp.route('/')
def schedule():
    conn = get_db_connection()
    cur = conn.cursor()

    # Получение списка групп
    cur.execute('SELECT group_id, group_name FROM Groups ORDER BY group_name;')
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