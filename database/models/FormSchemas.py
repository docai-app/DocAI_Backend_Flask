from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import UUID, TEXT, JSON, JSONB
from sqlalchemy import DateTime
from sqlalchemy.orm import declarative_base, relationship, backref
from ext import db

Base = declarative_base()


class FormSchemas(db.Model, Base):
    __tablename__ = 'form_schemas'
    id = db.Column(UUID , primary_key=True, unique=True, nullable=False, index=True)
    name = db.Column(TEXT, nullable=False)
    form_schema = db.Column(JSON, nullable=False, default=dict)
    ui_schema = db.Column(JSON, nullable=False, default=dict)
    data_schema = db.Column(JSONB, nullable=False, default=dict)
    description = db.Column(TEXT, nullable=True)
    updated_at = db.Column(DateTime, nullable=False, default=db.func.now())
    created_at = db.Column(DateTime, nullable=False, default=db.func.now())
    azure_form_model_id = db.Column(TEXT, nullable=True)
    is_ready = db.Column(db.Boolean, nullable=False, default=False)
    
    # forms_data = relationship("FormsData", back_populates="form_details")

    def __init__(self, id, name, form_schema, ui_schema, data_schema, description, updated_at, created_at, azure_form_model_id, is_ready):
        self.id = id
        self.name = name
        self.form_schema = form_schema
        self.ui_schema = ui_schema
        self.data_schema = data_schema
        self.description = description
        self.updated_at = updated_at
        self.created_at = created_at
        self.azure_form_model_id = azure_form_model_id
        self.is_ready = is_ready
        
    
    def __repr__(self):
        return "<FormSchemas(id='%s', name='%s', form_schema='%s', ui_schema='%s', data_schema='%s', description='%s', updated_at='%s', created_at='%s', azure_form_model_id='%s', is_ready='%s')>" % (self.id, self.name, self.form_schema, self.ui_schema, self.data_schema, self.description, self.updated_at, self.created_at, self.azure_form_model_id, self.is_ready)


