from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import UUID, ENUM, TEXT
from sqlalchemy import DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, relationship, backref
from ext import db


Base = declarative_base()


class DocumentsApproval(db.Model, Base):
    __tablename__ = 'documents_approval'
    id = db.Column(UUID , primary_key=True, unique=True, nullable=False, index=True)
    document_id = db.Column(UUID, ForeignKey('documents.id'), nullable=False, index=True)
    approved_by = db.Column(UUID, ForeignKey('users.id'), nullable=False, index=True)
    remark = db.Column(TEXT, nullable=True)
    status = db.Column(ENUM('awaiting', 'approved', 'rejected', name='document_approval_status_enum'), nullable=False, default='awaiting')
    updated_at = db.Column(DateTime, nullable=False, default=db.func.now())
    created_at = db.Column(DateTime, nullable=False, default=db.func.now())
    
    # document_details = relationship("Documents", back_populates="approval_details")
    # users = relationship("Users", back_populates="approval_details")

    def __init__(self, id, document_id, approved_by, remark, status, updated_at, created_at):
        self.id = id
        self.document_id = document_id
        self.approved_by = approved_by
        self.remark = remark
        self.status = status
        self.updated_at = updated_at
        self.created_at = created_at
    
    def __repr__(self):
        return "<DocumentsApproval(id='%s', document_id='%s', approved_by='%s', remark='%s', status='%s', updated_at='%s', created_at='%s')>" % (self.id, self.document_id, self.approved_by, self.remark, self.status, self.updated_at, self.created_at)
