from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import UUID, TEXT
from sqlalchemy import DateTime
from sqlalchemy.orm import declarative_base, relationship, backref
from ext import db


Base = declarative_base()


class Users(db.Model, Base):
    __tablename__ = 'users'
    id = db.Column(UUID, primary_key=True, unique=True, nullable=False)
    username = db.Column(TEXT, nullable=False, default='User')
    password = db.Column(TEXT, nullable=False)
    role = db.Column(TEXT, nullable=False, default='admin')
    description = db.Column(TEXT, nullable=True)
    last_active_at = db.Column(DateTime, nullable=False, default=db.func.now())
    updated_at = db.Column(DateTime, nullable=False, default=db.func.now())
    created_at = db.Column(DateTime, nullable=False, default=db.func.now())

    def __init__(self, id, username, password, role, description, last_active_at, updated_at, created_at):
        self.id = id
        self.username = username
        self.password = password
        self.role = role
        self.description = description
        self.last_active_at = last_active_at
        self.updated_at = updated_at
        self.created_at = created_at

    def __repr__(self):
        return "<User(id='%s', username='%s', password='%s', role='%s', description='%s', last_active_at='%s', updated_at='%s', created_at='%s')>" % (self.id, self.username, self.password, self.role, self.description, self.last_active_at, self.updated_at, self.created_at)
