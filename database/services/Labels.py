from database.models.Labels import Labels
from utils.model import row2dict, rows2dict
from ext import db
from datetime import datetime


class LabelsQueryService():
    @staticmethod
    def getAll():
        data = Labels.query.all()
        return rows2dict(data)

    @staticmethod
    def getSpecific(id):
        data = Labels.query.filter_by(id=id).first()
        return row2dict(data)

    @staticmethod
    def insert(name):
        try:
            data = Labels(name=name)
            db.session.add(data)
            db.session.commit()
            return True
        except Exception as e:
            print(e)
            return False

    @staticmethod
    def update(id, name):
        try:
            data = Labels.query.filter_by(id=id).first()
            data.name = name
            data.updated_at = datetime.now()
            db.session.add(data)
            db.session.commit()
            return True
        except Exception as e:
            print(e)
            return False