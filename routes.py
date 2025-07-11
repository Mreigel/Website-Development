from flask import Blueprint, render_template, redirect, request, url_for, flash, session
from sqlalchemy import or_, func
from werkzeug.utils import secure_filename
from models import db, User, Project, Message
from encryption import encrypt_field, decrypt_field
import os
import magic  # Requires python-magic-bin (Windows) or libmagic (Linux)
from datetime import datetime

routes = Blueprint('routes', __name__)

# --- Resume Upload Config ---
ALLOWED_EXTENSIONS = {'pdf'}
MAX_FILE_SIZE_MB = 5
UPLOAD_FOLDER = os.path.join('static', 'uploads', 'resumes')

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def is_pdf(file_path):
    file_type = magic.from_file(file_path, mime=True)
    return file_type == "application/pdf"

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
    messages = Message.query.order_by(Message.timestamp).all()

    return render_template(
        "admin.html",
        active_tab=active_tab,
        users=users,
        messages=messages,
        current_tab=tab
    )


@routes.route("/send_message", methods=["POST"])
def send_message():
    try:
        # Collect form fields
        name = request.form.get("name")
        email = request.form.get("email")
        skills = request.form.get("skills")
        experience = request.form.get("experience")
        github = request.form.get("github")
        portfolio = request.form.get("portfolio")
        availability = request.form.get("availability")
        message = request.form.get("message")
        resume = request.files.get("resume")

        # Resume validation
        if not resume or resume.filename == "":
            flash("Resume upload is required.", "error")
            return redirect(url_for("routes.join"))

        if not allowed_file(resume.filename) or not is_pdf(resume.stream):
            flash("Only valid PDF files are allowed.", "error")
            return redirect(url_for("routes.join"))

        # Save resume
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        save_path = os.path.join(UPLOAD_FOLDER, secure_filename(resume.filename))
        resume.save(save_path)

        # Optional: Save to DB or send admin alert here

        flash("Application submitted successfully!", "success")
        return redirect(url_for("routes.join"))

    except Exception as e:
        print("[ERROR] Join form submission failed:", str(e))  # Debug only
        flash("An error occurred while submitting your application.", "error")
        return redirect(url_for("routes.join"))
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
    # projects = Project.query.all()
    return render_template("projects.html")

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
        resume = request.files.get("resume")
        if not resume or resume.filename == "":
            flash("Resume upload is required.", "error")
            return redirect(url_for("routes.join"))

        if not allowed_file(resume.filename):
            flash("Only PDF files are allowed.", "error")
            return redirect(url_for("routes.join"))

        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        filename = secure_filename(resume.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        resume.save(filepath)

        if not is_pdf(filepath):
            os.remove(filepath)
            flash("Uploaded file is not a valid PDF.", "error")
            return redirect(url_for("routes.join"))

        if os.path.getsize(filepath) > MAX_FILE_SIZE_MB * 1024 * 1024:
            os.remove(filepath)
            flash("File exceeds size limit (5MB).", "error")
            return redirect(url_for("routes.join"))

        flash("Application submitted successfully!", "success")
        return redirect(url_for("routes.home"))

    return render_template("join.html")


@routes.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip().lower()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password')

        # New form fields
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()
        street = request.form.get('street', '').strip()
        city = request.form.get('city', '').strip()
        state = request.form.get('state', '').strip()
        zip_code = request.form.get('zip_code', '').strip()
        country = request.form.get('country', '').strip()

        users = User.query.all()
        for u in users:
            try:
                if u.email and decrypt_field(u._email).lower() == email:
                    flash("Email already in use.", "error")
                    return redirect(url_for('routes.register'))
            except Exception:
                continue

        if User.query.filter_by(username=username).first():
            flash("Username already taken.", "error")
            return redirect(url_for('routes.register'))

        new_user = User(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            street=street,
            city=city,
            state=state,
            zip_code=zip_code,
            country=country
        )
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

        user = None
        for u in User.query.all():
            try:
                if (u.email and decrypt_field(u._email).lower() == identifier) or u.username.lower() == identifier:
                    user = u
                    break
            except Exception:
                continue

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

    for u in User.query.all():
        try:
            if u.email and decrypt_field(u._email).lower() == new_email:
                flash("This email is already in use.", "error")
                return redirect(url_for('routes.account'))
        except Exception:
            continue

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

@routes.route("/request-password-reset", methods=["POST"])
def request_password_reset():
    email = request.form.get("email")
    # TODO: Implement email verification logic here
    flash("A password reset link will be sent to your email (when functionality is ready).", "info")
    return redirect(url_for("routes.account"))

@routes.route('/send-message', methods=['POST'])
def send_account_message():
    user_id = session.get('user_id')
    content = request.form.get('content', '').strip()
    context = request.form.get('context', 'inquiry')  # Default to 'inquiry'

    if context == "join_request":
        # Build structured message for Join form
        name = request.form.get('name')
        email = request.form.get('email')
        skills = request.form.get('skills')
        experience = request.form.get('experience')
        github = request.form.get('github')
        portfolio = request.form.get('portfolio')
        availability = request.form.get('availability')
        message = request.form.get('message')
        resume_file = request.files.get('resume')

        content = f"""🔹 New Join Request 🔹

Full Name: {name}
Email: {email}
Skills: {skills}
Experience Level: {experience}
GitHub: {github}
Portfolio: {portfolio}
Availability: {availability} hrs/week

Message:
{message or 'N/A'}
"""

        # Optionally: save or log `resume_file` here

        user = User.query.filter_by(email=email).first()
        sender_id = user.id if user else user_id or 0  # fallback if not logged in

    else:
        sender_id = user_id
        if not content:
            flash("Message cannot be empty.", "error")
            return redirect(url_for('routes.account'))

    # Save message
    new_msg = Message(
        sender_id=sender_id,
        content=content,
        is_from_admin=False,
        thread_id=sender_id,
        context=context
    )

    db.session.add(new_msg)
    db.session.commit()
    flash("Message sent to admin inbox.", "success")

    # Redirect appropriately
    return redirect(url_for('routes.home') if context == "join_request" else url_for('routes.account'))


@routes.route('/admin/reply', methods=['POST'])
def admin_reply():
    if 'user_id' not in session:
        flash("You must be logged in as an admin.", "warning")
        return redirect(url_for('routes.login'))

    admin = User.query.get(session['user_id'])
    if not admin or not admin.is_admin:
        flash("Access denied.", "danger")
        return redirect(url_for('routes.home'))

    thread_id = request.form.get('thread_id')
    content = request.form.get('content', '').strip()

    if not thread_id or not content:
        flash("Thread ID and message content are required.", "error")
        return redirect(url_for('routes.admin_dashboard', tab='inquiries'))

    try:
        thread_id = int(thread_id)
    except ValueError:
        flash("Invalid thread ID.", "error")
        return redirect(url_for('routes.admin_dashboard', tab='inquiries'))

    reply = Message(
        sender_id=admin.id,
        content=content,
        is_from_admin=True,
        thread_id=thread_id
    )

    db.session.add(reply)
    db.session.commit()
    flash("Reply sent successfully.", "success")
    return redirect(url_for('routes.admin_dashboard', tab='inquiries'))