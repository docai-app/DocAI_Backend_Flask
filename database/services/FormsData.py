from database.models.Documents import Documents
from database.models.FormsData import FormsData
from database.models.FormSchemas import FormSchemas
from utils.model import row2dict, rows2dict, rowsWithRelationship2dict
from ext import db
from sqlalchemy import cast, DATE
from datetime import datetime


class FormsDataQueryService():
    @staticmethod
    def getAll():
        data = FormsData.query.all()
        return rows2dict(data)

    @staticmethod
    def getSpecific(id):
        data = FormsData.query.filter_by(id=id).first()
        return row2dict(data)

    @staticmethod
    def insert(id, document_id, schema_id, data):
        try:
            data = FormsData(id=str(id), document_id=document_id, schema_id=schema_id,
                             data=data, updated_at=datetime.now(), created_at=datetime.now())
            db.session.add(data)
            db.session.commit()
            return row2dict(data)
        except Exception as e:
            print(e)
            return False

    @staticmethod
    def update(id, items):
        try:
            data = FormsData.query.filter_by(id=id).first()
            for key, value in items.items():
                setattr(data, key, value)
            data.updated_at = datetime.now()
            db.session.add(data)
            db.session.commit()
            return row2dict(data)
        except Exception as e:
            print(e)
            return False

    @staticmethod
    def getFormsByDate(date):
        data = FormsData.query.filter(
            cast(FormsData.created_at, DATE) == date).all()
        return rows2dict(data)

    @staticmethod
    def getFormsByLabelAndDate(label, date):
        FormSchemas = FormSchemas.query.filter(
            FormSchemas.name == label).first()
        data = FormsData.query.filter(cast(FormsData.created_at, DATE) == date).filter(
            FormsData.schema_id == FormSchemas.id).all()
        return [row2dict(FormSchemas), rowsWithRelationship2dict(data, ['document_details'])]
