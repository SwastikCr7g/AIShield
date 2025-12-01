# app/__init__.py
import os
from flask import Flask

def create_app():
    app = Flask(__name__)

    # Secret key
    app.config["SECRET_KEY"] = os.environ.get("FLASK_SECRET_KEY", "dev_secret_key")

    # Upload folder
    upload_folder = os.path.join(os.path.dirname(__file__), "static", "uploads")
    os.makedirs(upload_folder, exist_ok=True)
    app.config["UPLOAD_FOLDER"] = upload_folder

    # Import and register routes
    from app.routes import main   # <- make sure routes.py has `main = Blueprint(...)`
    app.register_blueprint(main)

    return app
