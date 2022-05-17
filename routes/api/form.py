from crypt import methods
import os
import json
from flask import Blueprint, jsonify, request, render_template, send_from_directory
from services.AzureForm import AzureFormService
from services.storage import StorageService
from services.form import FormService
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
load_dotenv()

form = Blueprint('form', __name__)

model_id = os.getenv("AZURE_ABSENCE_FORM_MODEL_ID")

ALLOWED_EXTENSIONS = set(['pdf', 'png', 'jpg', 'jpeg'])


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@form.route('/form/absence', methods=['POST'])
def labels():
    file = request.files.getlist('document[]')[0]
    print(file)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        formUrl = StorageService.upload(file, filename)
    res = AzureFormService.analysisForm(model_id, formUrl)
    result = FormService.mapAbsenceForm(res)
    print(result)
    return jsonify({'status': True, 'form_url': formUrl, 'result': result})


# @form.route('/labels/absence', methods=['POST'])
# def new():
#     requestData = request.get_json()
#     name = requestData['name']
#     DatabaseService.addNewLabel(name)
#     return jsonify({'status': 'Added'})
