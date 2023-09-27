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

@generate.route('/generate/smart_extraction/chart', methods=['POST'])
def generate_analysis():
    try:
        requestData = request.get_json()
        print(requestData)
        query = requestData['query']
        viewsName = requestData['views_name']
        tenant = requestData['tenant']
        dataSchema = requestData['data_schema']
        print(query, viewsName, tenant, dataSchema)
        result = GenerateService.generateChartFromDBData(viewsName, tenant, query, dataSchema)
        return jsonify({'status': True, 'result': result})
    except Exception as e:
        print(e)
        return jsonify({'status': False, 'message': 'Error: ' + str(e)})