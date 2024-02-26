from database.models.Documents import Documents
from utils.model import row2dict, rows2dict, getDocumentsLabel2dict
from ext import db
from datetime import datetime
# functions.py


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
    def insert(id, name, storage_url, content, status=0):
        try:
            data = Documents(
                id=str(id),
                name=name,
                storage_url=storage_url,
                content=content,
                status=status,
            )
            db.session.add(data)
            db.session.commit()
            return row2dict(data)
        except Exception as e:
            print(e)
            return False

    @staticmethod
    def update(id, items):
        try:
            data = Documents.query.filter_by(id=id).first()
            for key, value in items.items():
                setattr(data, key, value)
            data.updated_at = datetime.now()
            db.session.add(data)
            db.session.commit()
            return True
        except Exception as e:
            print(e)
            return False

    @staticmethod
    def getAllUploaded():
        data = Documents.query.filter_by(status='uploaded').all()
        return rows2dict(data)

    @staticmethod
    def getLatestUploaded():
        data = Documents.query.filter_by(status='uploaded').order_by(
            Documents.created_at.desc()).first()
        return row2dict(data)

    @staticmethod
    def getDocumentsLabel():
        try:
            data = db.session.execute(
                "SELECT DISTINCT D.label_id as id, L.name FROM documents as D LEFT JOIN labels AS L ON D.label_id = L.id").fetchall()
            return getDocumentsLabel2dict(data)
        except Exception as e:
            print(e)
            return False

    @staticmethod
    def getDocumentsByContent(content):
        data = Documents.query.filter(
            Documents.content.like('%' + content + '%')).all()
        return rows2dict(data)

    @staticmethod
    def getDocumentByName(name):
        data = Documents.query.filter(
            Documents.name.like('%' + name + '%')).all()
        return rows2dict(data)

    @staticmethod
    def getDocumentByLabelID(label_id):
        data = Documents.query.filter_by(label_id=label_id).all()
        return rows2dict(data)
