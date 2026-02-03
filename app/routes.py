#========================================================
# Bloque 1: IMPORTACIONES
#========================================================

from flask import Blueprint, render_template, url_for, flash, redirect, request, abort
from app import db
from app.models import User, Post


#=======================================================
# Bloque 2: CONFIGURACION DEL BLUEPRINT
#=======================================================
# El Bloeprint permite agrupar todas las rutas
# Bajo un mismo "Modulo logico" llamado main


main = Blueprint('main', __name__)


#=======================================================
# Bloque 3: AUTENTICACION DE USUARIOS
#=======================================================


#--------------------------------------
# Pagina principal (Lectura de posts)
#--------------------------------------

# RUTA 1: Inicio (Ver problemas)
@main.route("/")
@main.route("/home")
def home():
    
    # Consultamos todos los posts de la base de datos
    posts = Post.query.all()

    # Enviamos los datos al template (vista) para mostrarlos
    return render_template('index.html', posts=posts)


#-----------------------------------
# Registro de usuarios
#-----------------------------------

# RUTA 2: Registro
@main.route("/register", methods=['GET', 'POST'])
def register():

    # Si el usuario ya esta logueado, no debe registrarse otra vez
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    
    # Si el formulario fue enviado
    if request.method == 'POST':

        # Obtenemos los datos del formulario HTML
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Encriptamos password/contrasenha por seguridad
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        
        # Creamos y guardamos usuario en la BD
        user = User(username=username, email=email, password=hashed_password)

        db.session.add(user)
        db.session.commit()
        
        # Notificamos al usuario que el registro fue exitoso
        flash('Tu cuenta ha sido creada. ¡Ya puedes ingresar!', 'success')
        return redirect(url_for('main.login'))
    
    # SI el metodo es GET, mostramos el formulario de registro
    return render_template('register.html')


#------------------------------------------
# Inicio de sesion
#------------------------------------------

# RUTA 3: Login
@main.route("/login", methods=['GET', 'POST'])
def login():

    # Evitar el logeo si ya esta autenticado
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
        
    # Si el usuario envio el formulario de inicio de sesion
    if request.method == 'POST':
        
        # COMPLETAR LA LOGICA PARA EL LOGUEO MANHANA
        pass


    # Si es GEt o el login fallo, volvemos a mostrar el formulario
    return render_template('login.html')


#=======================================================
# Bloque 4: CRUD 
#=======================================================