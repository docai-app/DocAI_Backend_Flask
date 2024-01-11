from flask import Blueprint, jsonify, request
from services.ocr import OCRService

ocr = Blueprint('ocr', __name__)


@ocr.route('/alpha/ocr', methods=['POST'])
def document_ocr():
    try:
        # requestData = request.get_json()
        # document_url = requestData['document_url']
        document_url = request.form.get('document_url')
        # Print type of the document_url
        print(type(document_url))
        print("Document URL: ", str(document_url))
        content = OCRService.getText(document_url)
        print("Document Content: ", str(content))
        return jsonify({'status': True, 'result': content})
    except Exception as e:
        print(e)
        return jsonify({'status': False, 'message': 'Error: ' + str(e)})
