from database.models.Documents import Documents
from database.models.DocumentsApproval import DocumentsApproval
from database.models.FormsSchema import FormsSchema
from utils.model import row2dict, rows2dict
from ext import db
from datetime import datetime


class DocumentsApprovalQueryService():
    @staticmethod
    def getAll():
        data = DocumentsApproval.query.all()
        return rows2dict(data)

    @staticmethod
    def getSpecific(id):
        data = DocumentsApproval.query.filter_by(id=id).first()
        return row2dict(data)

    @staticmethod
    def insert(id, document_id, approved_by, status,):
        try:
            data = DocumentsApproval(id=str(id), document_id=document_id, approved_by=approved_by,
                                     status=status, updated_at=datetime.now(), created_at=datetime.now())
            db.session.add(data)
            db.session.commit()
            return row2dict(data)
        except Exception as e:
            print(e)
            pass
    
    @staticmethod 
    def update(id, items):
        try:
            data = DocumentsApproval.query.filter_by(id=id).first()
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
    def getDocumentsApprovalByStatus(status):
        data = DocumentsApproval.query.filter_by(status=status).all()
        return rows2dict(data)

    @staticmethod
    def getDocumentsApprovalByStatusAndFormsSchemaName(status, name):
        data = DocumentsApproval.query.filter_by(status=status).filter(
            Documents.id == DocumentsApproval.document_id).filter(FormsSchema.name == name).all()
        print(data)
        return rows2dict(data)
