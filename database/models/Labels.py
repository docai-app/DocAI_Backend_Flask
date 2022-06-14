from app import db
from sqlalchemy.dialects.postgresql import UUID, TEXT
from sqlalchemy import DateTime


class Labels(db.Model):
    __tablename__ = 'labels'
    id = db.Column(UUID , primary_key=True, unique=True, nullable=False)
    name = db.Column(TEXT, nullable=False)
    updated_at = db.Column(DateTime, nullable=False, default=db.func.now())
    created_at = db.Column(DateTime, nullable=False, default=db.func.now())

    def __init__(self, id, name, updated_at, created_at):
        self.id = id
        self.name = name
        self.updated_at = updated_at
        self.created_at = created_at
    
    def __repr__(self):
        return "<Label(id='%s', name='%s', updated_at='%s', created_at='%s')>" % (self.id, self.name, self.updated_at, self.created_at)


