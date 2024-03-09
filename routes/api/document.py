# File Path: routes/api/document.py

from flask import Blueprint, jsonify, request
from services.classification import ClassificationService
from flask_sqlalchemy import SQLAlchemy
from database.services.Documents import DocumentsQueryService
from services.document import DocumentService
from services.autogen import AutogenSerivce
import sys

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
        history = requestData['chat_history'] or ''
        answer, chat_history = DocumentService.qaDocuments(
            query, schema, metadata, history)
        return jsonify({'status': True, 'content': answer, 'chat_history': chat_history})
    except Exception as e:
        return jsonify({'status': False, 'message': str(e)})


@document.route('/documents/embedding/qa/suggestion', methods=['POST'])
def suggestion():
    try:
        requestData = request.get_json()
        schema = requestData['schema']
        metadata = requestData['metadata'] or {}
        answer = DocumentService.suggestionDocumentQA(schema, metadata)
        print("answer: ", answer)
        return jsonify({'status': True, 'suggestion': answer})
    except Exception as e:
        return jsonify({'status': False, 'message': str(e)})


@document.route('/documents/multiagent/qa', methods=['POST'])
def multiagentQA():
    # try:
    answer = "ok"
    chat_history = []

    # print(request.get_json(), file=sys.stdout)
    # import pdb
    # pdb.set_trace()
    requestData = request.get_json()
    query = requestData['query']
    schema = requestData['schema']
    metadata = requestData.get('metadata', {})
    smart_extraction_schemas = requestData['smart_extraction_schemas']
    history = requestData.get('chat_history', '')

    print(query, file=sys.stderr)
    print(schema, file=sys.stderr)
    print(metadata, file=sys.stderr)
    print("smart_extraction_schemas:")
    print(smart_extraction_schemas, file=sys.stderr)

    tool_metadata = {
        'query': query,
        'schema': schema,
        'metadata': metadata,
        'smart_extraction_schemas': smart_extraction_schemas,
        'history': history
    }

    print(metadata['document_ids'], file=sys.stderr)

    answer = AutogenSerivce.chat(tool_metadata)
    return jsonify({'status': True, 'content': answer})
    # except Exception as e:
    #     print("response error here", file=sys.stdout)
    #     return jsonify({'status': False, 'message': str(e)})
