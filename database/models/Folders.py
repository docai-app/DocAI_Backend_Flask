from app import db
from sqlalchemy.dialects.postgresql import UUID, TEXT
from sqlalchemy import DateTime


class Folders(db.Model):
    __tablename__ = 'folders'
    id = db.Column(UUID , primary_key=True, unique=True, nullable=False)
    name = db.Column(TEXT, nullable=False, default='New Folder')
    description = db.Column(TEXT, nullable=True)
    updated_at = db.Column(DateTime, nullable=False, default=db.func.now())
    created_at = db.Column(DateTime, nullable=False, default=db.func.now())

    def __init__(self, id, name, description, updated_at, created_at):
        self.id = id
        self.name = name
        self.description = description
        self.updated_at = updated_at
        self.created_at = created_at
    
    def __repr__(self):
        return "<Folder(id='%s', name='%s', description='%s', updated_at='%s', created_at='%s')>" % (self.id, self.name, self.description, self.updated_at, self.created_at)


