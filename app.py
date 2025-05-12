import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from flask_session import Session 
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_migrate import Migrate  # Importar Flask-Migrate

# Configure logging
logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

# create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "default_secret_key")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)  # needed for url_for to generate with https

# Configure the PostgreSQL database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", 
                                                      f"postgresql://{os.environ.get('PGUSER')}:{os.environ.get('PGPASSWORD')}@{os.environ.get('PGHOST')}:{os.environ.get('PGPORT', '5432')}/{os.environ.get('PGDATABASE')}")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# Configure session to use filesystem
app.config["SESSION_TYPE"] = "filesystem"
app.config["SESSION_PERMANENT"] = False

# Initialize the app with the extensions
db.init_app(app)
Session(app)

# Adicionar a configuração do Flask-Migrate
migrate = Migrate(app, db)  # Instancia o Migrate, associando o app e o db

with app.app_context():
    # Import models
    import models  # noqa: F401
    
    # Create database tables (se necessário, mas com migrações o recomendado é rodar os comandos de migração)
    # db.create_all()  # Não é mais necessário, pois usaremos migrações

    # Import and register routes
    from routes import register_routes
    register_routes(app)
