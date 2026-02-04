🛠️ Tecnologías Clave
Backend: Python con Flask 3.x.
Base de Datos: SQLAlchemy (ORM) con SQLite para desarrollo.
Seguridad: Flask-Bcrypt para encriptación de contraseñas y Flask-Login para gestión de sesiones.
Frontend: Bootstrap 5.3 y Jinja2 para una interfaz responsiva y dinámica.

Control de Versiones: Git y Flask-Migrate para migraciones de base de datos.

✨ Funcionalidades Desarrolladas
1. Sistema de Usuarios y Seguridad
Autenticación Robusta: Implementación de registro e inicio de sesión seguro.
Roles Diferenciados: Lógica separada para Ciudadanos y Administradores.
Protección de Datos: Hash de contraseñas y protección contra inyecciones SQL.

2. Para el Ciudadano (Frontend)
Gestión de Reportes: Capacidad para crear, editar y eliminar denuncias de problemas comunitarios.
Contacto Directo: Integración de enlaces directos a WhatsApp para facilitar la comunicación.
Interfaz Adaptable: Diseño 100% responsive que funciona en móviles y escritorio.

3. Panel de Administración (Backend)
Dashboard de Control: Vista exclusiva para administradores.
Moderación: Herramientas para gestionar usuarios y eliminar publicaciones inapropiadas.
Métricas: Visualización básica del estado de la plataforma.

4. API REST
Se implementó una API básica (/api/v1/problemas) que expone los datos de los reportes en formato JSON, permitiendo futuras integraciones con aplicaciones móviles o terceros.
📦 Ejecución Rápida

El proyecto requiere Python 3.8+.
Clonar el repositorio e instalar dependencias:

Bash
pip install -r requirements.txt
Configurar variables de entorno en un archivo .env.

Inicializar la base de datos y ejecutar:

Bash
flask db upgrade
python run.py

Desarrollado para la Hackathon Batch 5.0 Hecho con ❤️ en Paraguay
