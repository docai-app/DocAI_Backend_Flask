from app import db
from sqlalchemy.dialects.postgresql import UUID, TEXT, ENUM
from sqlalchemy import DateTime, ForeignKey


class Documents(db.Model):
    __tablename__ = 'documents'
    id = db.Column(UUID , primary_key=True, unique=True, nullable=False, index=True)
    name = db.Column(TEXT, nullable=False)
    label_id = db.Column(UUID, ForeignKey('labels.id'), nullable=True, index=True)
    storage_url = db.Column(TEXT, nullable=False)
    content = db.Column(TEXT, nullable=True)
    status = db.Column(ENUM('pending', 'uploaded', 'confirmed', name='document_status_enum'), nullable=False, default='pending')
    updated_at = db.Column(DateTime, nullable=False, default=db.func.now())
    created_at = db.Column(DateTime, nullable=False, default=db.func.now())

    def __init__(self, id, name, label_id, storage_url, content, status, updated_at, created_at):
        self.id = id
        self.name = name
        self.label_id = label_id
        self.storage_url = storage_url
        self.content = content
        self.status = status
        self.updated_at = updated_at
        self.created_at = created_at
    
    def __repr__(self):
        return "<Document(id='%s', name='%s', label_id='%s', storage_url='%s', content='%s', status='%s', updated_at='%s', created_at='%s')>" % (self.id, self.name, self.label_id, self.storage_url, self.content, self.status, self.updated_at, self.created_at)


