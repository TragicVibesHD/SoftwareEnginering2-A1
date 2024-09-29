from .models import *
from .views import *
from .controllers import *
from .main import *
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)

    # Configure your database URI
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///your-database.db'
    
    # Initialize the database with the app
    db.init_app(app)
    
    # Initialize Flask-Migrate
    migrate = Migrate(app, db)
    
    return app