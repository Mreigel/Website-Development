from flask import Blueprint, render_template, redirect, request, url_for, flash, session
from sqlalchemy import or_, func
from werkzeug.utils import secure_filename
from models import db, User, Project, Message
import os
from datetime import datetime

routes = Blueprint('routes', __name__)

# --- Context Processor ---
@routes.app_context_processor
def inject_globals():
    user = None
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
    return dict(current_user=user)

# --- Admin Routes ---
@routes.route('/admin')
def admin_dashboard():
    if 'user_id' not in session:
        flash("You must be logged in to access admin dashboard.", "warning")
        return redirect(url_for('routes.login'))

    user = User.query.get(session['user_id'])
    if not user or not user.is_admin:
        flash("Access denied.", "danger")
        return redirect(url_for('routes.account'))

    tab = request.args.get('tab', 'dashboard')
    tab_map = {
        'dashboard': 'partials/admin_home.html',
        'users': 'partials/admin_users.html',
        'inquiries': 'partials/admin_inquiries.html',
        'profile': 'partials/admin_profile.html',
        'security': 'partials/admin_security.html',
    }
    active_tab = tab_map.get(tab, 'partials/admin_home.html')
    users = User.query.order_by(User.created_at.desc()).all()
    return render_template("admin.html", active_tab=active_tab, users=users, current_tab=tab)

@routes.route('/admin/users')
def admin_users():
    if 'user_id' not in session:
        flash("You must be logged in to access admin tools.", "warning")
        return redirect(url_for('routes.login'))

    user = User.query.get(session['user_id'])
    if not user or not user.is_admin:
        flash("Access denied.", "danger")
        return redirect(url_for('routes.home'))

    all_users = User.query.order_by(User.created_at.desc()).all()
    return render_template('admin_users.html', users=all_users)

@routes.route('/admin/users/<int:user_id>', methods=['GET', 'POST'])
def admin_user_detail(user_id):
    if 'user_id' not in session:
        flash("You must be logged in.", "warning")
        return redirect(url_for('routes.login'))

    current = User.query.get(session['user_id'])
    if not current or not current.is_admin:
        flash("Access denied.", "danger")
        return redirect(url_for('routes.account'))

    user = User.query.get_or_404(user_id)
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        is_admin = bool(request.form.get('is_admin'))

        if not username or not email:
            flash("Username and email are required.", "error")
            return redirect(url_for('routes.admin_user_detail', user_id=user.id))

        user.username = username
        user.email = email
        user.is_admin = is_admin
        db.session.commit()
        flash("User info updated successfully.", "success")
        return redirect(url_for('routes.admin_user_detail', user_id=user.id))

    return render_template('admin_user_detail.html', user=user)

@routes.route('/admin/inquiries')
def view_inquiries():
    if 'user_id' not in session:
        return redirect(url_for('routes.login'))

    user = User.query.get(session['user_id'])
    if not user.is_admin:
        return redirect(url_for('routes.account'))

    messages = Message.query.order_by(Message.timestamp.desc()).all()
    return render_template('admin_inquiries.html', messages=messages)

# --- Public Routes ---
@routes.route('/')
def home():
    return render_template("home.html")

@routes.route('/about')
def about():
    return render_template("about.html")

@routes.route('/projects')
def projects():
    projects = Project.query.all()
    return render_template("projects.html", projects=projects)

@routes.route('/project/<int:project_id>')
def project_detail(project_id):
    project = Project.query.get_or_404(project_id)
    return render_template("project_detail.html", project=project)

@routes.route('/inquiry', methods=['GET', 'POST'])
def inquiry():
    if request.method == 'POST':
        flash("Inquiry submitted successfully!", "success")
        return redirect(url_for('routes.inquiry'))
    return render_template('inquiry.html')

@routes.route('/join', methods=['GET', 'POST'])
def join():
    if request.method == 'POST':
        resume = request.files.get('resume')
        if not resume:
            flash("Resume is required.", "error")
            return redirect(url_for('routes.join'))

        if not resume.filename.lower().endswith('.pdf'):
            flash("Only PDF files are allowed.", "error")
            return redirect(url_for('routes.join'))

        upload_dir = os.path.join('static', 'uploads')
        os.makedirs(upload_dir, exist_ok=True)
        save_path = os.path.join(upload_dir, secure_filename(resume.filename))
        resume.save(save_path)

        flash("Application submitted. We'll be in touch!", "success")
        return redirect(url_for('routes.join'))

    return render_template("join.html")

@routes.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip().lower()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password')

        if User.query.filter_by(username=username).first():
            flash("Username already taken.", "error")
            return redirect(url_for('routes.register'))

        if User.query.filter_by(email=email).first():
            flash("Email already in use.", "error")
            return redirect(url_for('routes.register'))

        new_user = User(username=username, email=email)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        flash("Account created! Please log in.", "success")
        return redirect(url_for('routes.login'))

    return render_template("sign-up.html")

@routes.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        identifier = request.form.get('username', '').strip().lower()
        password = request.form.get('password')

        user = User.query.filter(or_(func.lower(User.username) == identifier, func.lower(User.email) == identifier)).first()

        if user and user.check_password(password):
            session['user_id'] = user.id
            session['username'] = user.username
            flash(f"Welcome back, {user.username}!", "success")
            return redirect(url_for('routes.home'))
        else:
            flash('Invalid username/email or password.', 'error')
            return redirect(url_for('routes.login'))

    return render_template('login.html')

@routes.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    flash("You have been logged out.", "info")
    return redirect(url_for('routes.home'))

@routes.route('/account')
def account():
    if 'user_id' not in session:
        flash("You must be logged in to access account settings.", "warning")
        return redirect(url_for('routes.home'))

    user = User.query.get(session['user_id'])
    if not user:
        flash("User not found.", "danger")
        return redirect(url_for('routes.logout'))

    if user.is_admin:
        return redirect(url_for('routes.admin_dashboard'))

    return render_template('account.html', user=user)

@routes.route('/update_email', methods=['POST'])
def update_email():
    if 'user_id' not in session:
        flash("You must be logged in to change your email.", "warning")
        return redirect(url_for('routes.login'))

    new_email = request.form.get('new_email', '').strip().lower()
    user = User.query.get(session['user_id'])

    if not new_email:
        flash("New email is required.", "error")
        return redirect(url_for('routes.account'))

    if User.query.filter_by(email=new_email).first():
        flash("This email is already in use.", "error")
        return redirect(url_for('routes.account'))

    user.email = new_email
    db.session.commit()
    flash("Email updated. Verification logic coming soon.", "success")
    return redirect(url_for('routes.account'))

@routes.route('/update_password', methods=['POST'])
def update_password():
    if 'user_id' not in session:
        flash("You must be logged in to change your password.", "warning")
        return redirect(url_for('routes.login'))

    current_password = request.form.get('current_password')
    new_password = request.form.get('new_password')
    user = User.query.get(session['user_id'])

    if not user.check_password(current_password):
        flash("Current password is incorrect.", "error")
        return redirect(url_for('routes.account'))

    user.set_password(new_password)
    db.session.commit()
    flash("Password successfully updated.", "success")
    return redirect(url_for('routes.account'))

@routes.route('/update_profile', methods=['POST'])
def update_profile():
    if 'user_id' not in session:
        flash("Login required.", "warning")
        return redirect(url_for('routes.login'))

    user = User.query.get(session['user_id'])
    user.full_name = request.form.get('full_name')
    user.address = request.form.get('address')

    db.session.commit()
    flash("Profile updated.", "success")
    return redirect(url_for('routes.account'))

@routes.route('/send-message', methods=['POST'])
def send_account_message():
    if 'user_id' not in session:
        flash("You must be logged in.", "warning")
        return redirect(url_for('routes.login'))

    content = request.form.get('content', '').strip()
    if not content:
        flash("Message cannot be empty.", "error")
        return redirect(url_for('routes.account'))

    new_msg = Message(sender_id=session['user_id'], content=content)
    db.session.add(new_msg)
    db.session.commit()
    flash("Message sent successfully.", "success")
    return redirect(url_for('routes.account'))
