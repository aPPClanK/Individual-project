from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from utils import get_db_connection

groups_bp = Blueprint('groups', __name__)

@groups_bp.route('/')
def groups():
    group_id = request.args.get('group_id')
    student_id = request.args.get('student_id')
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute('SELECT course_id, course_name from Courses;')
    courses = cur.fetchall()
    
    cur.execute('''
        SELECT g.group_id, g.group_name, c.course_name, COUNT(s.student_id) AS student_count, c.course_id
        FROM Groups g
        LEFT JOIN Students s ON g.group_id = s.group_id
        INNER JOIN Courses c ON g.course_id = c.course_id
        GROUP BY g.group_id, g.group_name, c.course_name, c.course_id
        ORDER BY g.group_name;
    ''')
    groups = cur.fetchall()

    if group_id:
        cur.execute('''
            SELECT s.student_id, s.first_name, s.last_name, s.date_of_birth, s.gender, s.address, s.phone, s.email, g.group_name, g.group_id
            FROM Students s
            INNER JOIN Groups g ON s.group_id = g.group_id
            WHERE s.group_id = %s
            ORDER BY g.group_name, s.first_name;
        ''', (group_id,))
        show_all_students = False
    else:
        cur.execute('''
            SELECT s.student_id, s.first_name, s.last_name, s.date_of_birth, s.gender, s.address, s.phone, s.email, g.group_name
            FROM Students s
            INNER JOIN Groups g ON s.group_id = g.group_id
            ORDER BY g.group_name, s.first_name;
        ''')
        show_all_students = True

    students = cur.fetchall()

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

    return render_template(
        'groups.html',
        courses=courses,
        groups=groups,
        students=students,
        show_all_students=show_all_students,
        attendance=attendance,
        selected_group_id=group_id,
        selected_student_id=student_id
    )

@groups_bp.route('/add_group', methods=['POST'])
def add_group():
    group_name = request.form['group_name']
    course_id = request.form['course_id']
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('INSERT INTO Groups (group_name, course_id) VALUES (%s, %s);', (group_name, course_id))
    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for('groups.groups'))

@groups_bp.route('/delete_group/<int:group_id>', methods=['POST'])
def delete_group(group_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('DELETE FROM Groups WHERE group_id = %s;', (group_id,))
    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for('groups.groups'))

@groups_bp.route('/add_student', methods=['POST'])
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
    return redirect(url_for('groups.groups', group_id=group_id))

@groups_bp.route('/delete_student/<int:student_id>', methods=['POST'])
def delete_student(student_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('DELETE FROM Attendance WHERE student_id = %s;', (student_id,))
    cur.execute('DELETE FROM Students WHERE student_id = %s;', (student_id,))
    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for('groups.groups'))

@groups_bp.route('/edit_student', methods=['POST'])
def edit_student():
    student_id = request.form['student_id']
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    date_of_birth = request.form['date_of_birth']
    gender = request.form['gender']
    address = request.form['address']
    phone = request.form['phone']
    email = request.form['email']
    group_id = request.form['student_group_id']
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
        UPDATE Students
        SET first_name = %s, last_name = %s, date_of_birth = %s, gender = %s, address = %s, phone = %s, email = %s, group_id = %s
        WHERE student_id = %s;
    ''', (first_name, last_name, date_of_birth, gender, address, phone, email, group_id, student_id))
    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for('groups.groups', group_id=group_id))

@groups_bp.route('/edit_group', methods=['POST'])
def edit_group():
    group_id = request.form.get('group_id')
    group_name = request.form.get('group_name')
    course_id = request.form.get('course_id')
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
        UPDATE Groups
        SET group_name = %s, course_id = %s
        WHERE group_id = %s;
    ''', (group_name, course_id, group_id))
    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for('groups.groups'))

@groups_bp.route('/get_attendance')
def get_attendance():
    student_id = request.args.get('student_id')
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
        SELECT TO_CHAR(a.date, 'YYYY-MM-DD') AS date, s.subject_name, a.status, g.grade
        FROM Attendance a
        INNER JOIN Subjects s ON a.subject_id = s.subject_id
        LEFT JOIN Grades g ON a.student_id = g.student_id AND a.subject_id = g.subject_id AND a.date = g.date
        WHERE a.student_id = %s;
    ''', (student_id))
    attendance = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify(attendance)