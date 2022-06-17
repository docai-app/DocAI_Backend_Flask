from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy import DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, relationship, backref
from ext import db


Base = declarative_base()


class FormsData(db.Model, Base):
    __tablename__ = 'forms_data'
    id = db.Column(UUID , primary_key=True, unique=True, nullable=False, index=True)
    document_id = db.Column(UUID, ForeignKey('documents.id'), nullable=False, index=True)
    schema_id = db.Column(UUID, ForeignKey('forms_schema.id'), nullable=False, index=True)
    data = db.Column(JSONB, nullable=False, default=dict)
    updated_at = db.Column(DateTime, nullable=False, default=db.func.now())
    created_at = db.Column(DateTime, nullable=False, default=db.func.now())

    def __init__(self, id, document_id, schema_id, data, updated_at, created_at):
        self.id = id
        self.document_id = document_id
        self.schema_id = schema_id
        self.data = data
        self.updated_at = updated_at
        self.created_at = created_at
    
    def __repr__(self):
        return "<FormsData(id='%s', document_id='%s', schema_id='%s', data='%s', updated_at='%s', created_at='%s')>" % (self.id, self.document_id, self.schema_id, self.data, self.updated_at, self.created_at)


