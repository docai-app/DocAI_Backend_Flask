# File Path: routes/api/document.py

from flask import Blueprint, jsonify, request, render_template, send_from_directory
from services.classification import ClassificationService
from utils.model import row2dict, rows2dict
from flask_sqlalchemy import SQLAlchemy
from database.services.Documents import DocumentsQueryService
from services.document import DocumentService

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


@document.route('/documents/embedding', methods=['POST'])
def saveDocumentsEmbedding():
    try:
        requestData = request.get_json()
        document = requestData['document']
        schema = requestData['schema']
        res = DocumentService.saveDocument(document, schema)
        return jsonify({'status': res, 'message': 'Document saved'})
    except Exception as e:
        return jsonify({'status': False, 'message': str(e)})


@document.route('/documents/embedding/search', methods=['GET'])
def searchDocumentsEmbedding():
    try:
        requestData = request.get_json()
        query = requestData['query']
        schema = requestData['schema']
        metadata = requestData['metadata'] or {}
        res = DocumentService.similaritySearch(query, schema, metadata)
        return jsonify({'status': True, 'documents': res})
    except Exception as e:
        return jsonify({'status': False, 'message': str(e)})


@document.route('/documents/embedding/qa', methods=['POST'])
def qaDocuments():
    try:
        requestData = request.get_json()
        query = requestData['query']
        schema = requestData['schema']
        metadata = requestData['metadata'] or {}
        answer = DocumentService.qaDocuments(query, schema, metadata)
        return jsonify({'status': True, 'content': answer})
    except Exception as e:
        return jsonify({'status': False, 'message': str(e)})
