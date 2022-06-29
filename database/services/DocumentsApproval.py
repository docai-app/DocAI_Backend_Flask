from database.models.Documents import Documents
from database.models.DocumentsApproval import DocumentsApproval
from database.models.FormsData import FormsData
from database.models.FormsSchema import FormsSchema
from utils.model import row2dict, rows2dict, rowsWithRelationship2dict
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
    def getDocumentsApprovalWithFormsByStatusAndFormsSchemaName(status, name):
        data = Documents.query.filter(DocumentsApproval.document_id == Documents.id).filter(
            DocumentsApproval.status == status).filter(FormsSchema.name == name).all()
        return rowsWithRelationship2dict(data, ['approval_details', 'form_details'])

    @staticmethod
    def getDocumentsApprovalByStatusAndFormsSchemaName(status, name):
        data = DocumentsApproval.query.filter_by(status=status).filter(
            Documents.id == DocumentsApproval.document_id).filter(FormsSchema.name == name).all()
        return rowsWithRelationship2dict(data, ['document_details, forms_schema_details'])
