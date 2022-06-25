from crypt import methods
import json
from database.models.Labels import Labels
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


@classification.route('/documents/labels/<id>', methods=['GET'])
def documentsByLabelID(id):
    documents = DatabaseService.searchDocumentByLabelID(id)
    return jsonify({'documents': documents})
