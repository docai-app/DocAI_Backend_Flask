from database.models.Documents import Documents
from database.models.FormsData import FormsData
from database.models.FormSchemas import FormSchemas
from utils.model import row2dict, rows2dict, rowsWithRelationship2dict
from ext import db
from sqlalchemy import cast, DATE


class FormSchemasQueryService():
    @staticmethod
    def getAll():
        data = FormSchemas.query.all()
        return rows2dict(data)

    @staticmethod
    def getSpecific(id):
        data = FormSchemas.query.filter_by(id=id).first()
        return row2dict(data)

    @staticmethod
    def getFormSchemasByDate(date):
        data = FormSchemas.query.filter(
            cast(FormSchemas.created_at, DATE) == date).all()
        return rows2dict(data)

    @staticmethod
    def getFormSchemasByName(name):
        data = FormSchemas.query.filter(
            FormSchemas.name == name ).first()
        return row2dict(data)
    
    @staticmethod
    def getFormSchemasByModelId(model_id):
        data = FormSchemas.query.filter(
            FormSchemas.azure_form_model_id == model_id ).first()
        return row2dict(data)
