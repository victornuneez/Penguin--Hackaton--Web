from flask import Blueprint, render_template, url_for, flash, redirect, request, abort, jsonify
from . import db, bcrypt
from app.models import Rol, Usuario, Post
from flask_login import login_user, current_user, logout_user, login_required

main = Blueprint('main', __name__)

# --- INICIO Y AUTH ---

@main.route("/")
@main.route("/home")
def home():
    # Mostramos los reportes más recientes primero
    posts = Post.query.order_by(Post.date_posted.desc()).all() 
    return render_template('index.html', posts=posts)

@main.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        user_exists = Usuario.query.filter((Usuario.email == email) | (Usuario.username == username)).first()
        if user_exists:
            flash('El nombre de usuario o email ya están registrados.', 'warning')
            return redirect(url_for('main.register'))

        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        
        # id_rol=2 es 'Ciudadano'. Asegúrate de haber insertado este rol en la DB.
        user = Usuario(
            username=username, 
            email=email, 
            password=hashed_password, 
            id_rol=2
        )
        db.session.add(user)
        db.session.commit()
        
        flash('Cuenta creada con éxito. ¡Ya puedes ingresar!', 'success')
        return redirect(url_for('main.login'))
        
    return render_template('register.html')

@main.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
        
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = Usuario.query.filter_by(email=email).first()
        
        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('main.home'))
        else:
            flash('Login fallido. Revisa tus credenciales.', 'danger')
            
    return render_template('login.html')

@main.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('main.home'))

# --- GESTIÓN DE POSTS (CRUD) ---

@main.route("/post/new", methods=['GET', 'POST'])
@login_required 
def new_post():
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        contact = request.form.get('contact_info') or ""
        
        # Formateo de WhatsApp Paraguay
        contact = contact.replace(' ', '').replace('-', '').replace('(', '').replace(')', '').replace('+', '')
        if contact.startswith('0'):
            contact = '595' + contact[1:]
        
        # Usamos 'autor' porque así está en models.py
        new_post = Post(
            title=title, 
            content=content, 
            contact_info=contact, 
            autor=current_user
        )
        db.session.add(new_post)
        db.session.commit()

        flash('Tu reporte ha sido publicado.', 'success')
        return redirect(url_for('main.home'))
        
    return render_template('create.html')

@main.route("/post/<int:post_id>/update", methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    
    # Permiso: Solo autor o Admin (id_rol 1)
    if post.autor != current_user and current_user.id_rol != 1:
        abort(403)
    
    if request.method == 'POST':
        post.title = request.form.get('title')
        post.content = request.form.get('content')
        post.contact_info = request.form.get('contact_info')
        db.session.commit()
        flash('Actualizado correctamente.', 'success')
        return redirect(url_for('main.home'))
    
    return render_template('create.html', title='Editar Post', post=post)

@main.route("/post/<int:post_id>/delete", methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    
    # Permiso: Solo autor o Admin (id_rol 1)
    if post.autor != current_user and current_user.id_rol != 1:
        abort(403)
        
    db.session.delete(post)
    db.session.commit()
    flash('Publicación eliminada correctamente.', 'info')
    return redirect(url_for('main.home'))

# --- PANEL DE ADMINISTRACIÓN ---

@main.route("/admin/dashboard")
@login_required
def admin_dashboard():
    # Línea de diagnóstico: Mira tu terminal cuando intentes entrar
    print(f"DEBUG: El usuario {current_user.username} tiene id_rol: {current_user.id_rol}")

    # Verificamos que sea el ID 1 (Admin)
    if current_user.id_rol != 1:
        flash(f'Acceso denegado. Tu rol actual es {current_user.id_rol}, se requiere 1.', 'danger')
        return redirect(url_for('main.home'))
    
    usuarios = Usuario.query.all()
    total_posts = Post.query.count()
    return render_template('admin.html', usuarios=usuarios, total_posts=total_posts)

@main.route("/admin/cambiar_rol/<int:user_id>", methods=['POST'])
@login_required
def cambiar_rol(user_id):
    if current_user.id_rol != 1:
        abort(403)
    
    usuario = Usuario.query.get_or_404(user_id)
    
    # Evitar que el admin se cambie el rol a sí mismo
    if usuario.id_usuario == current_user.id_usuario:
        flash('No puedes cambiar tu propio rol.', 'warning')
        return redirect(url_for('main.admin_dashboard'))

    # Swapping entre admin (1) y ciudadano (2)
    usuario.id_rol = 2 if usuario.id_rol == 1 else 1
    db.session.commit()
    flash(f'Rol de {usuario.username} actualizado.', 'success')
    return redirect(url_for('main.admin_dashboard'))

@main.route("/admin/eliminar_usuario/<int:user_id>", methods=['POST'])
@login_required
def eliminar_usuario(user_id):
    if current_user.id_rol != 1:
        abort(403)
        
    usuario = Usuario.query.get_or_404(user_id)
    
    if usuario.id_usuario == current_user.id_usuario:
        flash('No puedes eliminar tu propia cuenta.', 'danger')
        return redirect(url_for('main.admin_dashboard'))
    
    # 1. Buscar todos los posts de este usuario
    posts_del_usuario = Post.query.filter_by(id_usuario=usuario.id_usuario).all()
    
    # 2. Borrarlos uno por uno
    for post in posts_del_usuario:
        db.session.delete(post)
    
    # 3. Ahora que el usuario no tiene posts "huérfanos", lo borramos a él
    db.session.delete(usuario)
    db.session.commit()
    
    flash(f'El usuario {usuario.username} y todos sus reportes han sido eliminados.', 'info')
    return redirect(url_for('main.admin_dashboard'))
# --- API ---

@main.route("/api/v1/problemas", methods=['GET'])
def get_problemas_api():
    posts = Post.query.all()
    output = []
    for post in posts:
        output.append({
            'id': post.id_post,
            'titulo': post.title,
            'contenido': post.content,
            'fecha': post.date_posted.strftime('%Y-%m-%d'),
            'autor': post.autor.username
        })
    return jsonify({'problemas': output})