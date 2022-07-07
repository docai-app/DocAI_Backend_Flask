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
    return jsonify({'documents': res})


@document.route('/documents/latest', methods=['GET'])
def getLatestUploaded():
    res = DocumentsQueryService.getLatestUploaded()
    if res:
        prediction = ClassificationService.predict(res['id'])
        return jsonify({'status': True, 'document': res, 'prediction': prediction})
    else:
        return jsonify({'status': True, 'document': None, 'prediction': None})


@document.route('/documents/labels', methods=['GET'])
def getDocumentsLabel():
    res = DocumentsQueryService.getDocumentsLabel()
    return jsonify({'labels': res})
