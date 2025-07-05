from flask import Flask, render_template, session, redirect, request, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from sqlalchemy import or_, func
import os

app = Flask(__name__)
app.secret_key = 'your_super_secret_key_here'
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'portfolio.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- Models ---

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=False)
    tech_stack = db.Column(db.String(120))
    image = db.Column(db.String(120))
    github_link = db.Column(db.String(255))
    live_demo_link = db.Column(db.String(255))


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(120), unique=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


# --- Routes ---

@app.route('/join', methods=['GET', 'POST'])
def join():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        github = request.form.get('github')
        portfolio = request.form.get('portfolio')
        resume = request.files.get('resume')

        if resume:
            filename = secure_filename(resume.filename)
            save_path = os.path.join('static/uploads', filename)
            resume.save(save_path)
            flash("Application submitted. We'll be in touch!", "success")
        else:
            flash("Resume is required.", "error")

        # Log or process further here

        return redirect(url_for('join'))

    return render_template("join.html")

@app.route('/')
def home():
    return render_template("home.html")

@app.route('/inquiry', methods=['GET', 'POST'])
def inquiry():
    if request.method == 'POST':
        # You can extract data here with request.form.get('name') etc.
        # Upload file logic can go here later
        flash("Inquiry submitted successfully!", "success")
        return redirect(url_for('inquiry'))
    return render_template('inquiry.html')


@app.route('/about')
def about():
    return render_template("about.html")


@app.route('/projects')
def projects():
    projects = Project.query.all()
    return render_template("projects.html", projects=projects)


@app.route('/project/<int:project_id>')
def project_detail(project_id):
    project = Project.query.get_or_404(project_id)
    return render_template("project_detail.html", project=project)


@app.route('/coming-soon')
def coming_soon():
    return render_template('coming_soon.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip().lower()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password')

        if User.query.filter_by(username=username).first():
            flash("Username already taken.", "error")
            return redirect(url_for('register'))

        if User.query.filter_by(email=email).first():
            flash("Email already in use.", "error")
            return redirect(url_for('register'))

        new_user = User(username=username, email=email)
        new_user.set_password(password)

        db.session.add(new_user)
        db.session.commit()

        flash("Account created! Please log in.", "success")
        return redirect(url_for('login'))

    return render_template("sign-up.html")


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        raw_identifier = request.form.get('username')
        password = request.form.get('password')
        identifier = raw_identifier.strip().lower()

        user = User.query.filter(
            or_(
                func.lower(User.username) == identifier,
                func.lower(User.email) == identifier
            )
        ).first()

        if user and user.check_password(password):
            session['user_id'] = user.id
            session['username'] = user.username
            flash(f"Welcome back, {user.username}!", "success")
            return redirect(url_for('home'))
        else:
            flash('Invalid username/email or password.', 'error')
            return redirect(url_for('login'))

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    flash('Logged out.', 'info')
    return redirect(url_for('home'))


@app.route('/account')
def account():
    if 'user_id' not in session:
        flash("You must be logged in to access account settings.", "warning")
        return redirect(url_for('home'))

    user = User.query.get(session['user_id'])
    return render_template('account.html', user=user)


# --- Helpers ---

@app.context_processor
def inject_globals():
    user = None
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
    return dict(current_user=user)


@app.shell_context_processor
def make_shell_context():
    return {
        'db': db,
        'Project': Project,
        'User': User
    }


# --- Seed if Needed ---
# --- Seed if Needed ---
if __name__ == '__main__':
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

    app.run(debug=True, host='0.0.0.0')  # Only runs locally

application = app
