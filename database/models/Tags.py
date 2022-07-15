from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import UUID, TEXT, INTEGER
from sqlalchemy import DateTime
from sqlalchemy.orm import declarative_base, relationship
from ext import db


Base = declarative_base()


class Tags(db.Model, Base):
    __tablename__ = 'tags'
    id = db.Column(INTEGER, primary_key=True, unique=True, nullable=False, autoincrement=True)
    name = db.Column(TEXT, nullable=True)
    updated_at = db.Column(DateTime, nullable=False, default=db.func.now())
    created_at = db.Column(DateTime, nullable=False, default=db.func.now())
    taggings_count = db.Column(INTEGER, nullable=True, default=0)
    
    # documents = relationship("Documents", back_populates="label_details")

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return "<Tags (id='%s', name='%s', updated_at='%s', created_at='%s' taggings_count='%s')>" % (self.id, self.name, self.updated_at, self.created_at, self.taggings_count)
