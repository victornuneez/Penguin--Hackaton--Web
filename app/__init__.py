import os
from dotenv import load_dotenv
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate

# Cargamos las variables del archivo .env
load_dotenv()

# Inicializamos las extensiones (herramientas)
db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    
    # CLAVE SECRETA: Necesaria para formularios seguros y sesiones
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

    # BASE DE DATOS: Se creará un archivo site.db en la carpeta
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Inicializamos las extensiones
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    
    # Configuración del login (a dónde ir si no estás logueado)
    login_manager.login_view = 'main.login' # Define a qué ruta Flask-login 
    login_manager.login_message_category = 'info'

    # Importamos y registramos las rutas (Blueprints)
    from app.routes import main
    app.register_blueprint(main)

    # Importamos los modelos AQUÍ para que Migrate los vea
    from .models import Usuario, Rol, Post

    # Definimos el loader, ahora que 'Usuario' ya existe en este contexto
    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(Usuario, int(user_id))

    return app