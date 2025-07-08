from flask import Flask, session
from flask_wtf.csrf import CSRFProtect
from datetime import datetime
import os

# --- App Setup ---
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'dev')

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'portfolio.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'


# --- Extensions ---
csrf = CSRFProtect()
csrf.init_app(app)

# --- Import models AFTER app setup ---
from models import db, User, Project, Message
db.init_app(app)

# --- Import routes AFTER models are loaded ---
from routes import routes
app.register_blueprint(routes, url_prefix='')

# --- Context Processors ---
@app.context_processor
def inject_globals():
    user = None
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
    return dict(current_user=user)

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'Project': Project, 'User': User}

# --- Sample Seed ---
with app.app_context():
    db.create_all()
    if not Project.query.first():
        sample_projects = [
            {
                "name": "E-Commerce Template",
                "description": "A modern online store built with Flask.",
                "tech_stack": "Flask, SQLite, HTML/CSS",
                "image": "project1.jpg",
                "github_link": "https://github.com/Mreigel/ecommerce-demo",
                "live_demo_link": "#"
            },
            {
                "name": "Freelancer Portfolio",
                "description": "A responsive portfolio website for showcasing personal projects.",
                "tech_stack": "HTML, CSS, JS",
                "image": "project2.jpg",
                "github_link": "https://github.com/Mreigel/portfolio",
                "live_demo_link": "#"
            }
        ]
        for p in sample_projects:
            db.session.add(Project(**p))
        db.session.commit()
        print("✅ Sample projects seeded.")

# --- WSGI Entrypoint ---
application = app

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
