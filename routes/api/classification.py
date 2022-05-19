from cProfile import label
from crypt import methods
import json
from flask import Blueprint, jsonify, request, render_template, send_from_directory
from services.classification import ClassificationService
from services.ocr import OCRService
from services.database import DatabaseService

classification = Blueprint('classification', __name__)


@classification.route('/classification/prepare', methods=['GET'])
def prepare():
    res = ClassificationService.prepare()
    return jsonify({'prediction': res})


@classification.route('/classification/initial', methods=['POST'])
def initial():
    files = request.json
    res = ClassificationService.initial(files['document'])
    return jsonify({'prediction': res})


@classification.route('/classification/predict', methods=['GET'])
def predict():
    id = request.args.get('id')
    res = ClassificationService.predict(id)
    return jsonify({'label': res})


@classification.route('/classification/confirm', methods=['POST'])
def confirm():
    requestData = request.get_json()
    id = requestData['id']
    label = requestData['label']
    res = ClassificationService.confirm(id, label)
    return jsonify({'status': res})


@classification.route('/labels', methods=['GET'])
def labels():
    res = DatabaseService.getAllLabel()
    return jsonify({'prediction': res})


@classification.route('/documents')
def documents():
    res = DatabaseService.getAllDoucment()
    return jsonify({'prediction': res})


@classification.route('/documents/lastest')
def lastest():
    document = DatabaseService.getAndPredictLastestDoucment()
    if document:
        prediction = ClassificationService.predict(document['id'])
        return jsonify({'document': document, 'prediction': prediction})
    else:
        return jsonify({'status': 'null'})


@classification.route('/documents/uploaded')
def uploadedDocuments():
    res = DatabaseService.getAllUploadedDocument()
    return jsonify({'documents': res})
