from database.models.Documents import Documents
from database.models.FormsData import FormsData
from database.models.FormsSchema import FormsSchema
from utils.model import row2dict, rows2dict, rowsWithRelationship2dict
from ext import db
from sqlalchemy import cast, DATE


class FormsSchemaQueryService():
    @staticmethod
    def getAll():
        data = FormsSchema.query.all()
        return rows2dict(data)

    @staticmethod
    def getSpecific(id):
        data = FormsSchema.query.filter_by(id=id).first()
        return row2dict(data)

    @staticmethod
    def getFormsSchemaByDate(date):
        data = FormsSchema.query.filter(
            cast(FormsSchema.created_at, DATE) == date).all()
        return rows2dict(data)

    @staticmethod
    def getFormsSchemaByName(name):
        data = FormsSchema.query.filter(
            FormsSchema.name == name ).first()
        return row2dict(data)
