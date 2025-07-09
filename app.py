import os
import json
import boto3
import logging
from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from flask_migrate import Migrate
from models import db, User, Project, Message
from dotenv import load_dotenv
from botocore.exceptions import ClientError

# --- Load local .env for local dev
load_dotenv()

# --- App Setup
app = Flask(__name__)
csrf = CSRFProtect()

# --- Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- DB Setup
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

    session_boto = boto3.session.Session()
    client = session_boto.client(service_name='secretsmanager', region_name=region_name)

    try:
        get_secret_value_response = client.get_secret_value(SecretId=secret_name)
        secret_data = json.loads(get_secret_value_response['SecretString'])
    except ClientError as e:
        logger.error(f"❌ Failed to retrieve secret: {e}")
        raise

    app.secret_key = secret_data.get("secret_key", os.urandom(24))
    username = secret_data['username']
    password = secret_data['password']
    host = os.environ.get("DB_HOST")
    port = os.environ.get("DB_PORT", "5432")
    dbname = os.environ.get("DB_NAME", "postgres")

    if not all([host, port, dbname]):
        raise RuntimeError("❌ Missing DB_HOST, DB_PORT, or DB_NAME")

    app.config['SQLALCHEMY_DATABASE_URI'] = (
        f"postgresql://{username}:{password}@{host}:{port}/{dbname}"
    )

# --- Common Config
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# --- Init Extensions
db.init_app(app)
csrf.init_app(app)
migrate = Migrate(app, db)

# --- Register routes
from routes import routes
app.register_blueprint(routes, url_prefix='')

# --- Global user context
@app.context_processor
def inject_globals():
    user = None
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
    return dict(current_user=user)

# --- Health Check
@app.route("/health")
def health():
    return "OK", 200

# --- Flask Shell
@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'Project': Project, 'User': User}

# --- Entrypoint
application = app

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
