import sqlite3
import uuid
from datetime import datetime
from flask import g

DATABASE = 'database/database.db'


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        # Enable foreign key check
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
    def updateDocumentStatusAndLabbel(id, status, label):
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
    def addNewDocument(name, storage, content):
        print(
            str(uuid.uuid4()),
            name,
            storage,
            content,
            'uploaded',
            str(datetime.now())
        )
        db = get_db()
        cursor = db.cursor()
        document = cursor.execute("INSERT INTO documents (id,name,storage,content,status,created_at) VALUES (?,?,?,?,?,?)", (
            str(uuid.uuid4()),
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
            "SELECT * FROM documents WHERE content LIKE ?", ['%'+content+'%'])
        return documents

    @staticmethod
    def searchDocumentByName(name):
        documents = query_db(
            "SELECT * FROM documents WHERE name LIKE ?", ['%'+name+'%'])
        return documents

    @staticmethod
    def countEachLabelDocumentByDate(date):
        documents = query_db(
            "SELECT D.label, L.name, COUNT(D.id) as count FROM documents AS D LEFT JOIN labels AS L ON D.label = L.id WHERE D.created_at LIKE ? GROUP BY D.label ORDER BY COUNT(D.id) DESC", ['%'+date+'%'])
        return documents
