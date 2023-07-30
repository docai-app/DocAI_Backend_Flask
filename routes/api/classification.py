import json
from database.models.Labels import Labels
from database.services.Documents import DocumentsQueryService
from flask import Blueprint, jsonify, request, render_template, send_from_directory
from services.classification import ClassificationService
from services.ocr import OCRService
from services.database import DatabaseService
import numpy


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
    print("Model name: ", request.args.get('model'))
    content = request.args.get('content')
    model = request.args.get('model') or 'public'
    res = ClassificationService.predict(content, model)
    return jsonify({'label_id': res})


@classification.route('/classification/confirm', methods=['POST'])
def confirm():
    try:
        requestData = request.get_json()
        content = requestData['content']
        label = requestData['label']
        model = requestData['model'] or 'public'
        print(content, label, model)
        print(type(label))
        # if label type is string, convert it to array. On the other hand, if label type is array, just keep it.
        if type(label) == str:
            label = numpy.array([label])
        elif type(label) == list:
            label = numpy.array(label)
        res = ClassificationService.confirm(content, label, model)
        return jsonify({'status': res, 'message': 'Document confirmed'})
    except Exception as e:
        return jsonify({'status': False, 'message': str(e)})


@classification.route('/documents/labels/<id>', methods=['GET'])
def documentsByLabelID(id):
    try:
        res = DocumentsQueryService.getDocumentByLabelID(id)
        return jsonify({'status': True, 'documents': res})
    except Exception as e:
        print(e)
        return jsonify({'status': False, 'message': 'Error: ' + str(e)})
