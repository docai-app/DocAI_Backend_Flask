import json
import os
from crypt import methods

from database.models.DocumentsApproval import DocumentsApproval
from dotenv import load_dotenv
from flask import (Blueprint, jsonify, render_template, request,
                   send_from_directory)
from services.AzureForm import AzureFormService
from services.database import DatabaseService
from services.form import FormService
from services.storage import StorageService
from werkzeug.utils import secure_filename

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
    formData = FormService.addNewFormData(
        absenceFormData, '請假表', document['id'])
    documentsApproval = FormService.addNewDocumentsApproval(
        document['id'], 'a305f520-2a36-4f3b-8bab-72113e04f355')
    return jsonify({'status': True, 'form_url': document['storage'], 'form_id': formData['id'], 'result': absenceFormData})


@form.route('/form/<id>', methods=['PUT'])
def updateFormDataByID(id):
    requestData = request.get_json()
    form = requestData['form']
    res = FormService.updateFormDataByID(id, form)
    return jsonify({'status': 'success'})


# Get Absence Form By Approval Status Parameters API
# API example: localhost:8888/form/absence/approval?status=<status>
# function: getAbsenceFormByApprovalStatus
# input: status
# output: list of Absence Form Data
@form.route('/form/absence/approval', methods=['GET'])
def getAbsenceFormByApprovalStatus():
    status = request.args.get('status')
    forms = DatabaseService.getFormsDataByApprovalStatus(status)
    return jsonify({'status': True, 'forms': forms})
