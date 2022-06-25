from email.policy import default
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import UUID, TEXT, INTEGER
from sqlalchemy import DateTime
from sqlalchemy.orm import declarative_base, relationship
from ext import db


Base = declarative_base()


class Labels(db.Model, Base):
    __tablename__ = 'labels'
    id = db.Column(INTEGER, primary_key=True, unique=True, nullable=False, autoincrement=True)
    name = db.Column(TEXT, nullable=False)
    updated_at = db.Column(DateTime, nullable=False, default=db.func.now())
    created_at = db.Column(DateTime, nullable=False, default=db.func.now())
    
    documents = relationship("Documents", back_populates="label_details")

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return "<Label (id='%s', name='%s', updated_at='%s', created_at='%s')>" % (self.id, self.name, self.updated_at, self.created_at)
