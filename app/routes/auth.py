from flask import Blueprint, render_template, request, redirect, url_for, session, flash

auth_bp = Blueprint('auth', __name__, template_folder='templates')

DEAN_PASSWORD = 'dean_password_123'

# Маршрут для авторизации
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        password = request.form['password']
        if password == DEAN_PASSWORD:
            session['authorized'] = True
            return redirect('/')
        else:
            flash('Неверный пароль. Попробуйте снова.')
    return render_template('auth.html')

# Маршрут для выхода из системы
@auth_bp.route('/logout')
def logout():
    session.pop('authorized', None)
    flash('Вы вышли из системы.')
    return redirect(url_for('auth.login'))
