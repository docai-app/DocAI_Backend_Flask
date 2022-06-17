from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import UUID, TEXT
from sqlalchemy import DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, relationship, backref
from ext import db


Base = declarative_base()


class Roles(db.Model, Base):
    __tablename__ = 'roles'
    id = db.Column(UUID, primary_key=True, unique=True, nullable=False)
    role = db.Column(TEXT, nullable=False, default='admin')
    description = db.Column(TEXT, nullable=True)
    updated_at = db.Column(DateTime, nullable=False, default=db.func.now())
    created_at = db.Column(DateTime, nullable=False, default=db.func.now())
    
    users = relationship("Users", back_populates="role_details")

    def __init__(self, id, role, description, updated_at, created_at):
        self.id = id
        self.role = role
        self.description = description
        self.updated_at = updated_at
        self.created_at = created_at

    def __repr__(self):
        return "<Roles(id='%s', role='%s', description='%s', updated_at='%s', created_at='%s')>" % (self.id, self.role, self.description, self.updated_at, self.created_at)
