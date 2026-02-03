# Importamos las herramientas necesarias
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from flask_login import UserMixin
from . import db

# Creamos la tabla rol
class Rol(db.Model):
    # Nombre de la tabla
    __tablename__ = 'rol'

    # Columnas de la tabla rol
    id_rol = Column(Integer, primary_key=True, autoincrement=True)
    descripcion = Column(String(30), nullable=False)

    # Relacion con la tabla usuario
    usuario = relationship('usuario', back_populates='rol')

class Usuario(db.Model, UserMixin):
    # Nombre de la tabla
    __tablename__ = 'usuario'

    # Columnas de la tabla usuario
    id_usuario = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(20), nullable=False, unique=True)
    nombre_apellido = Column(String(120), nullable=False)
    password = Column(String(20), nullable=False)
    email = Column(String(120), nullable=False)

    # Clave foranea hacia la tabla rol
    id_rol = Column(Integer, ForeignKey('rol.id_rol'), nullable=False)

    # Relaciones con las tablas rol y post
    rol = relationship('Rol', back_populates='usuario')
    post = relationship('Post', back_populates='autor')

    def get_id(self):
        return str(self.id_usuario)

class Post(db.Model):
    # Nombre de la tabla
    __tablename__ = 'post'

    # Columnas de la tabla post
    id_post = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(100), nullable=False)
    date_posted = Column(DateTime, nullable=False, default=datetime.utcnow)
    content = Column(Text, nullable=False)
    contact_info = Column(String(100), nullable=False)

    # Clave foranea a la tabla usuario
    id_usuario = Column(Integer, ForeignKey('usuario.id_usuario'), nullable=False)

    # Relacion con la tabla usuario
    autor = relationship('Usuario', back_populates='post')
