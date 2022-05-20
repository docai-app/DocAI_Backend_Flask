from math import e
import sqlite3
import uuid
from datetime import datetime
from flask import g
import json

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
    def getAllDoucment():
        documents = query_db("SELECT * FROM documents")
        return documents

    @staticmethod
    def getDoucmentByID(id):
        documents = query_db(
            "SELECT * FROM documents WHERE id==?", [id], True)
        return documents

    @staticmethod
    def getAndPredictLastestDoucment():
        documents = query_db(
            "SELECT * FROM documents WHERE status=='uploaded' ORDER BY created_at DESC LIMIT 1", one=True)
        return documents

    @staticmethod
    def getAllUploadedDocument():
        documents = query_db(
            "SELECT * FROM documents WHERE status=='uploaded'")
        return documents

    @staticmethod
    def getAllLabel():
        labels = query_db("SELECT * FROM labels")
        return labels

    @staticmethod
    def getLabelByID(id):
        labels = query_db("SELECT * FROM labels WHERE id==?", [str(id)], True)
        return labels

    @staticmethod
    def addNewLabel(name):
        db = get_db()
        cursor = db.cursor()
        label = cursor.execute("INSERT INTO labels (name,created_at) VALUES (?,?)", (
            name,
            str(datetime.now())
        ))
        db.commit()
        return label

    @staticmethod
    def updateDocumentStatusAndLabel(id, status, label):
        db = get_db()
        cursor = db.cursor()
        cursor.execute("UPDATE documents SET status = ? , label = ? WHERE id = ?", [
            status,
            str(label),
            str(id)
        ])
        db.commit()
        return cursor

    @staticmethod
    def addNewDocument(id, name, storage, content):
        db = get_db()
        cursor = db.cursor()
        document = cursor.execute("INSERT INTO documents (id,name,storage,content,status,created_at) VALUES (?,?,?,?,?,?)", (
            str(id),
            name,
            storage,
            content,
            "uploaded",
            str(datetime.now())
        ))
        db.commit()
        return document

    @staticmethod
    def searchDocumentByContent(content):
        documents = query_db(
            "SELECT * FROM documents WHERE content LIKE ?", ['%' + content + '%'])
        return documents

    @staticmethod
    def searchDocumentByName(name):
        documents = query_db(
            "SELECT * FROM documents WHERE name LIKE ?", ['%' + name + '%'])
        return documents

    @staticmethod
    def countEachLabelDocumentByDate(date):
        documents = query_db(
            "SELECT D.label, L.name, COUNT(D.id) as count FROM documents AS D LEFT JOIN labels AS L ON D.label = L.id WHERE D.created_at LIKE ? GROUP BY D.label ORDER BY COUNT(D.id) DESC", ['%'+date+'%'])
        return documents

    @staticmethod
    def getFormSchemaByName(name):
        formSchema = query_db(
            "SELECT * FROM forms_schema WHERE name LIKE ?", ['%' + name + '%'], one=True)
        return formSchema

    @staticmethod
    def addNewFormData(result, name):
        try:
            formSchema = DatabaseService.getFormSchemaByName(name)
            formDataID = str(uuid.uuid4())
            db = get_db()
            cursor = db.cursor()
            cursor.execute("INSERT INTO forms_data (id,schema_id,data,updated_at,created_at) VALUES (?,?,?,?,?)", (
                formDataID,
                formSchema['id'],
                json.dumps(result),
                str(datetime.now()),
                str(datetime.now())
            ))
            db.commit()
            newFormData = DatabaseService.getFormDataByID(formDataID)
            return newFormData
        except Exception(e):
            print(e)
            pass

    @staticmethod
    def getFormDataByID(id):
        formData = query_db(
            "SELECT * FROM forms_data WHERE id==?", [id], True)
        return formData
    
    @staticmethod
    def updateFormDataByID(id, data):
        db = get_db()
        cursor = db.cursor()
        cursor.execute("UPDATE forms_data SET data = ? , updated_at = ? WHERE id = ?", [
            json.dumps(data),
            str(datetime.now()),
            str(id)
        ])
        db.commit()
        return cursor