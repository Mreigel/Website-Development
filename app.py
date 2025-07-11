import os
import json
import boto3
import logging
from flask import Flask, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from flask_migrate import Migrate
from models import db, User, Project, Message
from encryption import set_encryption_key
from dotenv import load_dotenv
from botocore.exceptions import ClientError

load_dotenv()

app = Flask(__name__)
csrf = CSRFProtect()

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Determine database type
USE_SQLITE = os.getenv("USE_SQLITE") == "true"

if USE_SQLITE:
    app.secret_key = os.getenv("SECRET_KEY", os.urandom(24))
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///portfolio.db'
else:
    secret_name = os.environ.get("RDS_SECRET_NAME")
    region_name = os.environ.get("AWS_REGION", "us-west-1")

    if not secret_name:
        logger.error("❌ Missing RDS_SECRET_NAME in environment")
        raise RuntimeError("Missing RDS_SECRET_NAME")

    # Fetch DB credentials
    session_boto = boto3.session.Session()
    client = session_boto.client(service_name='secretsmanager', region_name=region_name)

    try:
        secret_response = client.get_secret_value(SecretId=secret_name)
        secret_data = json.loads(secret_response['SecretString'])
    except ClientError as e:
        logger.error(f"❌ Failed to retrieve secret: {e}")
        raise

    app.secret_key = secret_data.get("secret_key", os.urandom(24))

    # Fetch encryption key from Secrets Manager
    try:
        enc_response = client.get_secret_value(SecretId="c2c/encryption")
        encryption_key = json.loads(enc_response["SecretString"]).get("encryption_key")
        set_encryption_key(encryption_key)
    except Exception as e:
        logger.error("❌ Failed to load encryption_key", exc_info=True)
        raise RuntimeError("Missing ENCRYPTION_KEY in Secrets Manager")

    username = secret_data['username']
    password = secret_data['password']
    host = os.environ.get("DB_HOST")
    port = os.environ.get("DB_PORT", "5432")
    dbname = os.environ.get("DB_NAME", "postgres")

    if not all([host, port, dbname]):
        raise RuntimeError("❌ Missing DB_HOST, DB_PORT, or DB_NAME")

    app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql://{username}:{password}@{host}:{port}/{dbname}"

# Global config
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# Initialize extensions
csrf.init_app(app)
db.init_app(app)
migrate = Migrate(app, db)

# Register routes
from routes import routes
app.register_blueprint(routes, url_prefix='')

@app.context_processor
def inject_globals():
    user = None
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
    return dict(current_user=user)

@app.route("/")
def index():
    return "App is running!", 200

@app.route("/health")
def health():
    return "OK", 200


@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404


@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Project': Project, 'Message': Message}

@app.errorhandler(Exception)
def handle_exception(e):
    logger.error("Unhandled Exception", exc_info=True)
    return jsonify({"message": "An internal error occurred."}), 500

@app.after_request
def add_security_headers(response):
    response.headers['Content-Security-Policy'] = (
        "default-src 'self'; "
        "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://cdn.jsdelivr.net; "
        "font-src 'self' https://fonts.gstatic.com data:; "
        "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net;"
    )
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    return response



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
