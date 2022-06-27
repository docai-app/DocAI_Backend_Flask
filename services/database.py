import json
import uuid
from datetime import datetime
from math import e

from sqlalchemy.sql import func
from database.services.FormsSchema import FormsSchemaQueryService
from utils.model import row2dict, rows2dict, countEachLabelDocumentByDate2dict

from database.models.FormsData import FormsData
from database.models.FormsSchema import FormsSchema
from database.models.Labels import Labels
from ext import db


class DatabaseService():
    @staticmethod
    def getFormSchemaByName(name):
        # formSchema = query_db(
        #     "SELECT * FROM forms_schema WHERE name LIKE ?", ['%' + name + '%'], one=True)
        formSchema = FormsSchema.query.filter(
            FormsSchema.name.like(f'%{name}%')).first()
        return row2dict(formSchema)

    @staticmethod
    def getFormDataByID(id):
        # formData = query_db(
        #     "SELECT * FROM forms_data WHERE id==?", [id], True)
        formData = FormsData.query.filter_by(id=id).first()
        return row2dict(formData)

    @staticmethod
    def searchFormByLabelAndDate(label, date):
        # formSchema = query_db(
        #     "SELECT * FROM forms_schema WHERE name LIKE ?", ['%' + label + '%'], one=True)
        formSchema = FormsSchema.query.filter(
            FormsSchema.name.like(f'%{label}%')).first()
        print(formSchema)
        # formData = query_db(
        #     "SELECT *, D.storage FROM forms_data AS F JOIN documents AS D ON F.document_id = D.id WHERE F.schema_id==? AND F.created_at LIKE ?", [formSchema['id'], '%'+date+'%'])
        formData = db.session.execute(
            "SELECT F, D.storage_url FROM forms_data AS F JOIN documents AS D ON F.document_id = D.id WHERE F.schema_id==:id AND CAST(F.created_at AS DATE) = :date", {"id": formSchema.id, "date": date}).all()
        print(formData)
        return {'form_schema': row2dict(formSchema), 'form_data': formData}

    @staticmethod
    def updateFormDataByID(id, data):
        # db = get_db()
        # cursor = db.cursor()
        # cursor.execute("UPDATE forms_data SET data = ? , updated_at = ? WHERE id = ?", [
        #     json.dumps(data),
        #     str(datetime.now()),
        #     str(id)
        # ])
        # db.commit()
        # return cursor

        try:
            formdata = FormsData.query.filter_by(id=id).first()
            formdata.data = json.dumps(data)
            formdata.updated_at = datetime.now()
            db.commit()
            return {"status": True}
        except:
            return {"status": False}
