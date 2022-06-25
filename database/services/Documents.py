from database.models.Documents import Documents
from utils.model import row2dict, rows2dict
from ext import db
from datetime import datetime


class DocumentsQueryService():
    @staticmethod
    def getAll():
        data = Documents.query.all()
        return rows2dict(data)

    @staticmethod
    def getSpecific(id):
        data = Documents.query.filter_by(id=id).first()
        return row2dict(data)

    @staticmethod
    def insert(id, name, storage_url, content):
        try:
            data = Documents(
                id=str(id),
                name=name,
                label_id=None,
                storage_url=storage_url,
                content=content,
                status="uploaded",
                updated_at=datetime.now(),
                created_at=datetime.now()
            )
            db.session.add(data)
            db.session.commit()
            return data
        except Exception as e:
            print(e)
            return False

    @staticmethod
    def getAllUploaded():
        data = Documents.query.filter_by(status='uploaded').all()
        return rows2dict(data)

    @staticmethod
    def getLastestUploaded():
        data = Documents.query.filter_by(status='uploaded').order_by(
            Documents.created_at.desc()).first()
        print(data)
        return row2dict(data)
