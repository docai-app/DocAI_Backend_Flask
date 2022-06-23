from database.models.Documents import Documents
from utils.model import row2dict, rows2dict

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
    def getAllUploaded():
        data = Documents.query.filter_by(status='uploaded').all()
        return rows2dict(data)
    
    @staticmethod
    def getAndPredictLastest():
        data = Documents.query.filter_by(status='uploaded').order_by(
            Documents.created_at.desc()).limit(1).first()
        return row2dict(data)