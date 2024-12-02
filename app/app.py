import os
from flask import Flask
from routes.news import news_bp
from routes.groups import groups_bp
from routes.schedule import schedule_bp
from routes.teachers import teachers_bp

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SK')

app.register_blueprint(news_bp, url_prefix='/')
app.register_blueprint(groups_bp, url_prefix='/groups')
app.register_blueprint(schedule_bp, url_prefix='/schedule')
app.register_blueprint(teachers_bp, url_prefix='/teachers')

if __name__ == '__main__':
    app.run(debug=True)