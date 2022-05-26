from crypt import methods
import os
import json
from flask import Blueprint, jsonify, request, render_template, send_from_directory
from services.AzureForm import AzureFormService
from services.database import DatabaseService
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
        document = StorageService.upload(file, filename)
    res = AzureFormService.analysisForm(model_id, document['storage'])
    absenceFormData = FormService.mapAbsenceForm(res)
    formData = FormService.addNewFormData(absenceFormData, '請假表', document['id'])
    return jsonify({'status': True, 'form_url': document['storage'], 'form_id': formData['id'], 'result': absenceFormData})


@form.route('/form/<id>', methods=['PUT'])
def updateFormDataByID(id):
    requestData = request.get_json()
    form = requestData['form']
    res = FormService.updateFormDataByID(id, form)
    return jsonify({'status': 'success'})
