import json
import sqlite3
import uuid
from datetime import datetime
from math import e

from flask import g
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
from utils.model import row2dict, rows2dict, countEachLabelDocumentByDate2dict

from database.models.Documents import Documents
from database.models.FormsData import FormsData
from database.models.FormsSchema import FormsSchema
from database.models.Labels import Labels
from ext import db

# db = SQLAlchemy()
DATABASE = 'database/database.db'


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        # Enable foreign key check
        db.row_factory = dict_factory
        db.execute("PRAGMA foreign_keys = ON")
    return db


def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv


class DatabaseService():
    @staticmethod
    def countEachLabelDocumentByDate(date):
        data = db.session.execute("SELECT D.label_id, L.name, COUNT(D.id) as count FROM documents AS D LEFT JOIN labels AS L ON D.label_id = L.id WHERE CAST(D.created_at AS DATE) = :date GROUP BY (D.label_id, L.name) ORDER BY COUNT(D.id) DESC", {
                                  'date': date}).fetchall()
        return countEachLabelDocumentByDate2dict(data)

    @staticmethod
    def getFormSchemaByName(name):
        # formSchema = query_db(
        #     "SELECT * FROM forms_schema WHERE name LIKE ?", ['%' + name + '%'], one=True)
        formSchema = FormsSchema.query.filter(
            FormsSchema.name.like(f'%{name}%')).first()
        return row2dict(formSchema)

    @staticmethod
    def addNewFormData(result, name, documentID):
        try:
            formSchema = DatabaseService.getFormSchemaByName(name)
            formDataID = str(uuid.uuid4())
            # db = get_db()
            # cursor = db.cursor()
            # cursor.execute("INSERT INTO forms_data (id,document_id,schema_id,data,updated_at,created_at) VALUES (?,?,?,?,?,?)", (
            #     formDataID,
            #     documentID,
            #     formSchema['id'],
            #     json.dumps(result),
            #     str(datetime.now()),
            #     str(datetime.now())
            # ))
            # db.commit()
            formdata = FormsData(
                id=formDataID,
                document_id=documentID,
                schema_id=formSchema['id'],
                data=json.dumps(result),
                updated_at=datetime.now(),
                created_at=datetime.now()
            )
            db.add(formdata)
            db.commit()
            newFormData = DatabaseService.getFormDataByID(formDataID)
            return newFormData
        except Exception(e):
            print(e)
            pass

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
