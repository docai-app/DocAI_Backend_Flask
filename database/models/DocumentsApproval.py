from app import db
from sqlalchemy.dialects.postgresql import UUID, ENUM
from sqlalchemy import DateTime, ForeignKey


class DocumentsApproval(db.Model):
    __tablename__ = 'documents_approval'
    id = db.Column(UUID , primary_key=True, unique=True, nullable=False, index=True)
    document_id = db.Column(UUID, ForeignKey('documents.id'), nullable=False, index=True)
    approved_by = db.Column(UUID, ForeignKey('users.id'), nullable=False, index=True)
    status = db.Column(ENUM('awaiting', 'approved', 'rejected', name='document_approval_status_enum'), nullable=False, default='awaiting')
    updated_at = db.Column(DateTime, nullable=False, default=db.func.now())
    created_at = db.Column(DateTime, nullable=False, default=db.func.now())

    def __init__(self, id, document_id, approved_by, status, updated_at, created_at):
        self.id = id
        self.document_id = document_id
        self.approved_by = approved_by
        self.status = status
        self.updated_at = updated_at
        self.created_at = created_at
    
    def __repr__(self):
        return "<DocumentsApproval(id='%s', document_id='%s', approved_by='%s', status='%s', updated_at='%s', created_at='%s')>" % (self.id, self.document_id, self.approved_by, self.status, self.updated_at, self.created_at)


