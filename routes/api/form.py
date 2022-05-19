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
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        formUrl = StorageService.upload(file, filename)
    res = AzureFormService.analysisForm(model_id, formUrl)
    absenceFormData = FormService.mapAbsenceForm(res)
    formData = FormService.addNewFormData(absenceFormData, '請假表')
    print(absenceFormData)
    print(formData)
    return jsonify({'status': True, 'form_url': formUrl, 'form_id': formData['id'], 'result': absenceFormData})


# @form.route('/labels/absence', methods=['POST'])
# def new():
#     requestData = request.get_json()
#     name = requestData['name']
#     DatabaseService.addNewLabel(name)
#     return jsonify({'status': 'Added'})
