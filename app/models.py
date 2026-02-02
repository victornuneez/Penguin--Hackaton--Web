# Importamos las herramientas necesarias
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from flask_login import UserMixin
from . import db

# Creamos la tabla rol
class Rol(db.model):
    # Nombre de la tabla
    __tablename__ = 'rol'

class Usuario(db.Model, UserMixin):
    # Nombre de la tabla
    __tablename__ = 'usuario'

class Post(db.Model):
    # Nombre de la tabla
    __tablename__ = 'post'
