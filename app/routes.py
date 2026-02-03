"""
DOCUMENTACIÓN DE LÓGICA DE RUTAS Y CONTROLADORES (routes.py)
-----------------------------------------------------------
Este archivo gestiona las peticiones HTTP y decide qué respuesta enviar al usuario.
Utiliza 'Blueprints' para organizar las rutas de la aplicación.

FLUJO GENERAL DE LAS RUTAS:

1. GESTIÓN DE USUARIOS (Auth):
    - Registro: Captura datos, encripta la contraseña con Bcrypt y guarda en DB.
    - Login: Valida credenciales contra la DB y crea una sesión de usuario.
    - Logout: Destruye la sesión activa.
    - Seguridad: Usa '@login_required' para proteger rutas que necesitan cuenta.

2. SISTEMA DE PUBLICACIONES (CRUD):
    - Create (Crear): 'new_post' recibe datos del formulario y los vincula al 'current_user'.
    - Read (Leer): 'home' consulta todos los problemas y los renderiza en el muro.
    - Update (Editar): 'update_post' verifica que el editor sea el dueño o un admin.
    - Delete (Borrar): 'delete_post' elimina el registro físicamente de la base de datos.

3. INTEROPERABILIDAD (API):
    - Endpoint JSON: 'get_problemas_api' permite que otras aplicaciones lean 
    nuestros datos en un formato estándar (JSON) sin ver el HTML.

LÓGICA DE SEGURIDAD APLICADA:
- En todas las rutas de edición/borrado, se aplica una validación doble:
    ¿Es el autor del post? O ¿Es un administrador? Si ambas son falsas, se bloquea.
-----------------------------------------------------------
"""

"""
DOCUMENTACIÓN DE GESTIÓN ADMINISTRATIVA (Panel de Control)
-----------------------------------------------------------
Esta ruta es el "Cerebro de Supervisión" del sistema.

FLUJO DE SEGURIDAD:
1. BLOQUEO DE ACCESO: Usa '@login_required' para asegurar que el visitante esté logueado.
2. VALIDACIÓN DE ROL: Verifica si 'current_user.role' es exactamente 'admin'.
    - Si no es admin: Lo expulsa al inicio con un mensaje de error.
    - Si es admin: Le permite ver la lista de todos los usuarios registrados.

OBJETIVO: Permitir que el gobierno o la organización vea cuántos ciudadanos 
están registrados y quiénes son.
-----------------------------------------------------------
"""
#========================================================
# Bloque 1: IMPORTACIONES
#========================================================
# * Aqui se importan todas las herramientas necesarias:
# - FLask para manejo de rutas y respuestas.
# - Base de datos y encriptacion.
# - Modelos del sistema.
# - Gestion de sesiones de usuario.


from flask import Blueprint, render_template, url_for, flash, redirect, request, abort
from app import db, bcrypt
from app.models import User, Post
from flask_login import login_user, current_user, logout_user, login_required
from flask import jsonify


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
        
        # Capturamos credenciales enviadas desde el formularo
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Buscamos al usuario por su email
        user = User.query.filter_by(email=email).first()
        
        # Verificamos si el usuario existe y la contraseña coincide
        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('main.home'))
        else:
            flash('Login fallido. Revisa correo y contraseña', 'danger')
    
    # Si es GEt o el login fallo, volvemos a mostrar el formulario
    return render_template('login.html')


#=======================================================
# Bloque 4: CRUD 
#=======================================================

#------------------------------------------
# EDITAR PUBLICACIÓN EXISTENTE
#------------------------------------------

@main.route("/post/<int:post_id>/update", methods=['GET', 'POST'])
@login_required
def update_post(post_id):

    # Buscamos el post o devolvemos error 404
    post = Post.query.get_or_404(post_id)

    # Seguridad: Solo el autor o un admin pueden editar
    if post.author != current_user and current_user.role != 'admin':
        flash('No tienes permiso para editar esto', 'danger')
        return redirect(url_for('main.home'))
    
    # Si se envio el formulario de edicion
    if request.method == 'POST':

        # Actualizamos los campos del formulario
        post.title = request.form.get('title')
        post.content = request.form.get('content')
        post.contact_info = request.form.get('contact_info')

        # Guardamos cambios
        db.session.commit()

        # Informamos al usuario que los cambios fueron guardados
        flash('¡Publicación actualizada!', 'success')
        return redirect(url_for('main.home'))
    
    # Cargamos el formulario con los datos actuales del post
    return render_template('create.html', title='Editar Post', post=post)

#------------------------------------------
# BORRAR PUBLICACIÓN
#------------------------------------------

@main.route("/post/<int:post_id>/delete", methods=['POST'])
@login_required
def delete_post(post_id):

    # Obtenemos el post a eliminar o lanzamos error 404 si no existe
    post = Post.query.get_or_404(post_id)

    # SEGURIDAD: Solo el autor O un administrador pueden borrar
    if post.author != current_user and current_user.role != 'admin':
        flash('Acción no permitida', 'danger')
    
    else:  # Eliminar la publicacion
        db.session.delete(post)
        db.session.commit()
        flash('Publicación eliminada', 'info')
    
    # Redirigimos a la pagina principal
    return redirect(url_for('main.home'))

#------------------------------------------
# Cerrar sesion
#------------------------------------------

# RUTA 4: Logout
@main.route("/logout")
def logout():

    # Flask-Login elimina la sesion activa
    logout_user()
    return redirect(url_for('main.home'))

#------------------------------------------
# Crear publicacion
#------------------------------------------

# RUTA 5: Crear Nuevo Problema (Requiere login)
@main.route("/post/new", methods=['GET', 'POST'])
@login_required 
def new_post():

    # Creacion del CRUD
    if request.method == 'POST':
        
        # Obtenemos los datos de los campos
        title = request.form.get('title')
        content = request.form.get('content')
        contact = request.form.get('contact_info') # Capturamos el contacto
        
        # Creamos un objeto Post, realacionado al usuario actual
        post = Post(title=title, content=content, contact_info=contact, author=current_user)

        # Guardamos el post con el nuevo campo
        db.session.add(post)
        db.session.commit()
        
        # Confirmamos al ususario que su publicacion ya es visible
        flash('Tu voz ha sido escuchada. El problema está publicado.', 'success')
        return redirect(url_for('main.home'))
    
    # Lo dirigimos al formulario para crear problemas
    return render_template('create.html')

#=======================================================
# Bloque 5: API PUBLICA 
#=======================================================

@main.route("/api/v1/problemas", methods=['GET'])
def get_problemas_api():

    # Obtenemos todos los posts
    posts = Post.query.all()

    # Convertimos los objetos de la DB a una lista de diccionarios tipo (JSON)
    output = []

    # recorremos cada post para transformalos en estructura JSON
    for post in posts:
        output.append({
            'id': post.id,
            'titulo': post.title,
            'contenido': post.content,
            'autor': post.author.username
        })
    
    # Retornamos la informacion en formato JSON para que otras app puedan hacer acciones sin depender del HTML
    return jsonify({'problemas': output})

"""
DOCUMENTACIÓN DEL FLUJO: CAMBIO DE ROL (Gestión Administrativa)
------------------------------------------------------------
1. SEGURIDAD: Verifica que quien hace clic sea ADMIN y esté logueado.
2. CAPTURA: Recibe el ID del usuario que queremos modificar.
3. LÓGICA DE CAMBIO:
    - Si el usuario es 'user', lo asciende a 'admin'.
    - Si el usuario ya es 'admin', lo baja a 'user'.
4. PERSISTENCIA: Guarda el cambio en la DB y avisa con un mensaje Flash.
------------------------------------------------------------
"""

#=======================================================
# Bloque 6: ADMINISTRACION DE ROLES
#=======================================================

@main.route("/admin/cambiar_rol/<int:user_id>", methods=['POST'])
@login_required
def cambiar_rol(user_id):

    # Solo los administradores pueden acceder
    if current_user.role != 'admin':
        abort(403) # Prohibido para no-admins
    
    # Buscamos al usuario  objetivo, y si no lo encotramos, soltamos erro 404
    usuario = User.query.get_or_404(user_id)
    
    # Evitar que el admin se quite el permiso a sí mismo por error
    if usuario.id == current_user.id:
        flash('No podés cambiar tu propio rol.', 'warning')
        return redirect(url_for('main.admin_dashboard'))

    # Cambiamos el rol del usuario
    if usuario.role == 'admin':
        usuario.role = 'user'
        flash(f'Rol de {usuario.username} cambiado a Ciudadano.', 'info')
    else:
        usuario.role = 'admin'
        flash(f'Rol de {usuario.username} cambiado a Administrador.', 'success')
    
    # Guardamos en la BD el cambio de rol
    db.session.commit()
    return redirect(url_for('main.admin_dashboard'))


#=======================================================
# bloque 7: PANEL DE GESTION PRINCIPAL
#=======================================================
# * Esta ruta funciona como centro de control del sistema
# - permite al administrador:
# - Ver todos los usuarios registrados
# - Obtener Cantidad de posts
# - Acceder a acciones de moderacion ()

#---------------------------------------------
# Cargar datos y estadisticas de la app
#---------------------------------------------
@main.route("/admin/dashboard")
@login_required
def admin_dashboard():

    # SEGURIDAD: Solo el administrador puede entrar aquí
    if current_user.role != 'admin':
        flash('Acceso denegado. Se requieren permisos de administrador.', 'danger')

        # Si es un usuario normal, se le redirige al inicio
        return redirect(url_for('main.home'))
    
    # Consultamos todos los usuarios para mostrar estadísticas
    usuarios = User.query.all()
    total_posts = Post.query.count()
    
    # Enviamos al templates, para Mostrar la lista de ususarios y cantidad de publicaciones totales
    return render_template('admin.html', usuarios=usuarios, total_posts=total_posts)



"""
DOCUMENTACIÓN DE FLUJO: ELIMINACIÓN DE USUARIOS
----------------------------------------------
1. AUTORIZACIÓN: Verifica que el ejecutor sea ADMIN.
2. PROTECCIÓN: Comprueba que el usuario a borrar NO sea el mismo admin logueado.
3. LIMPIEZA: Al borrar un usuario, Flask-SQLAlchemy (según la relación definida)
podría borrar sus posts o dejarlos huérfanos. 
4. FINALIZACIÓN: Elimina el registro y redirige con un mensaje informativo.
----------------------------------------------
"""

#---------------------------------------------
# Eliminacion de usuarios
#---------------------------------------------

@main.route("/admin/eliminar_usuario/<int:user_id>", methods=['POST'])
@login_required
def eliminar_usuario(user_id):

    # Solo un adminitrador puede acceder, si no lo es salta error 403
    if current_user.role != 'admin':
        abort(403)

    # Buscamos al usuario objetivo a eleminar, de no encontrarlo error 404
    usuario = User.query.get_or_404(user_id)
    
    # Seguridad: Impide que un administrador se borre a si mismo (suicidio de cuenta)
    if usuario.id == current_user.id: 
        flash('No podés eliminar tu propia cuenta de administrador.', 'danger')
        return redirect(url_for('main.admin_dashboard'))
    
    # Se borra el usuario de la base datos
    db.session.delete(usuario)

    # Confirmamos los cambios de forma permanente
    db.session.commit()

    # Mostramos un mensaje de confirmacion de la eliminacion
    flash(f'El usuario {usuario.username} ha sido expulsado del sistema.', 'info')

    # Redireccionamos al panel de administracion
    return redirect(url_for('main.admin_dashboard'))