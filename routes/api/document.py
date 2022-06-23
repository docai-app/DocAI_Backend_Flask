from crypt import methods
import uuid
from flask import Blueprint, jsonify, request, render_template, send_from_directory
from services.classification import ClassificationService
from utils.model import row2dict, rows2dict
from flask_sqlalchemy import SQLAlchemy
from database.services.Documents import DocumentsQueryService

db = SQLAlchemy()
document = Blueprint('document', __name__)


@document.route('/documents', methods=['GET'])
def getAll():
    res = DocumentsQueryService.getAll()
    return jsonify({'documents': res})


@document.route('/documents/<id>', methods=['GET'])
def getSpecific(id):
    res = DocumentsQueryService.getSpecific(id)
    return jsonify({'document': res})


@document.route('/documents/uploaded')
def getAllUploaded():
    res = DocumentsQueryService.getAllUploaded()
    print(res)
    return jsonify({'documents': res})


@document.route('/documents/lastest', methods=['GET'])
def lastest():
    document = DocumentsQueryService.getAndPredictLastest()
    print(document)
    if document:
        prediction = ClassificationService.predict(document['id'])
        return jsonify({'document': document, 'prediction': prediction})
    else:
        return jsonify({'status': 'null'})