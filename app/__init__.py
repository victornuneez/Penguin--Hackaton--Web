import os
from dotenv import load_dotenv
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt

# Cargamos las variables del archivo .env
load_dotenv()

# Inicializamos las extensiones (herramientas)
db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    
    # CLAVE SECRETA: Necesaria para formularios seguros y sesiones
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

    # BASE DE DATOS: Se creará un archivo site.db en la carpeta
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db' # No quiero tocar todavía, hasta que pueda vincular directamente con el sql
    # app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL') # Cuando eso esté hecho, le podemos asignar de esta forma para que quede más seguro
    
    # Inicializamos las extensiones
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    
    # Configuración del login (a dónde ir si no estás logueado)
    login_manager.login_view = 'main.login' # Define a qué ruta Flask-login 
    login_manager.login_message_category = 'info'

    # Importamos y registramos las rutas (Blueprints)
    from app.routes import main
    app.register_blueprint(main)

    # Creamos las tablas de la DB si no existen
    with app.app_context():
        db.create_all()

    return app