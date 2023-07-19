from flask import Blueprint, jsonify, request
from services.ocr import OCRService
from services.generate import GenerateService

generate = Blueprint('generate', __name__)


@generate.route('/generate/chart', methods=['POST'])
def generate_chart():
    try:
        query = request.form.get('query')
        content = request.form.get('content')
        # Print type of the document_url
        result = GenerateService.generateChart(query, content)
        return jsonify({'status': True, 'result': result})
    except Exception as e:
        print(e)
        return jsonify({'status': False, 'message': 'Error: ' + str(e)})
