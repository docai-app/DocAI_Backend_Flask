from database.models.Tags import Tags
from utils.model import row2dict, rows2dict
from ext import db
from datetime import datetime


class TagsQueryService():
    @staticmethod
    def getAll():
        data = Tags.query.all()
        return rows2dict(data)

    @staticmethod
    def getSpecific(id):
        data = Tags.query.filter_by(id=int(id)).first()
        return row2dict(data)
