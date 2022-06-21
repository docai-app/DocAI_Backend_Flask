from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, relationship, backref
from ext import db


Base = declarative_base()


class DocumentFolder(db.Model, Base):
    __tablename__ = 'document_folder'
    id = db.Column(UUID, primary_key=True, unique=True,
                   nullable=False, index=True)
    document_id = db.Column(UUID, ForeignKey(
        'documents.id'), nullable=False, index=True)
    folder_id = db.Column(UUID, ForeignKey('folders.id'),
                          nullable=False, index=True)
    updated_at = db.Column(DateTime, nullable=False, default=db.func.now())
    created_at = db.Column(DateTime, nullable=False, default=db.func.now())
    
    folder_details = relationship("Folders", back_populates="document_folder")
    documents = relationship("Documents", back_populates="folder_details")

    def __init__(self, id, document_id, folder_id, updated_at, created_at):
        self.id = id
        self.document_id = document_id
        self.folder_id = folder_id
        self.updated_at = updated_at
        self.created_at = created_at

    def __repr__(self):
        return "<DocumentFolder(id='%s', document_id='%s', folder_id='%s', updated_at='%s', created_at='%s')>" % (self.id, self.document_id, self.folder_id, self.updated_at, self.created_at)
