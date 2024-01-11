from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import UUID, TEXT, INTEGER
from sqlalchemy import DateTime
from sqlalchemy.orm import declarative_base, relationship
from ext import db


Base = declarative_base()


class Taggings(db.Model, Base):
    __tablename__ = 'taggings'
    id = db.Column(UUID, primary_key=True, unique=True,
                   nullable=False, autoincrement=True)
    tag_id = db.Column(INTEGER, db.ForeignKey('tags.id'), nullable=True)
    taggable_type = db.Column(TEXT, nullable=True)
    taggable_id = db.Column(UUID, db.ForeignKey('documents.id'), nullable=True)
    tagger_type = db.Column(TEXT, nullable=True)
    tagger_id = db.Column(UUID, db.ForeignKey('users.id'), nullable=True)
    context = db.Column(TEXT, nullable=True)
    updated_at = db.Column(DateTime, nullable=False, default=db.func.now())
    created_at = db.Column(DateTime, nullable=False, default=db.func.now())
    tenant = db.Column(TEXT, nullable=True)

    # documents = relationship("Documents", back_populates="label_details")

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return "<Taggings (id='%s', tag_id='%s', taggable_type='%s', taggable_id='%s', tagger_type='%s', tagger_id='%s', context='%s', updated_at='%s', created_at='%s', tenant='%s')>" % (self.id, self.tag_id, self.taggable_type, self.taggable_id, self.tagger_type, self.tagger_id, self.context, self.updated_at, self.created_at, self.tenant)
