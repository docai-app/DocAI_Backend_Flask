import os
import uuid
from database.models.FormsSchema import FormsSchema
from database.services.DocumentsApproval import DocumentsApprovalQueryService
from database.services.FormsData import FormsDataQueryService
from database.services.FormsSchema import FormsSchemaQueryService
from flask import Blueprint, jsonify, request, render_template, send_from_directory
from services.AzureForm import AzureFormService
from services.database import DatabaseService
from services.form import FormService
from services.storage import StorageService
from werkzeug.utils import secure_filename


form = Blueprint('form', __name__)

model_id = os.getenv("AZURE_ABSENCE_FORM_MODEL_ID")

ALLOWED_EXTENSIONS = set(['pdf', 'png', 'jpg', 'jpeg'])


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@form.route('/form/absence', methods=['POST'])
def labels():
    try:
        file = request.files.getlist('document[]')[0]
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            document = StorageService.upload(file, filename)
        res = AzureFormService.analysisForm(model_id, document['storage_url'])
        absenceFormData = FormService.mapAbsenceForm(res)
        formSchema = FormsSchemaQueryService.getFormsSchemaByName('請假表')
        formData = FormsDataQueryService.insert(uuid.uuid4(),
                                                document['id'], formSchema['id'], absenceFormData)
        print(formData)
        documentApproval = DocumentsApprovalQueryService.insert(
            uuid.uuid4(), document['id'], 'a305f520-2a36-4f3b-8bab-72113e04f355', 'awaiting')
        return jsonify({'status': True, 'form_url': document['storage_url'], 'form_id': formData['id'], 'result': absenceFormData, 'approval': documentApproval})
    except Exception as e:
        print(e)
        return jsonify({'status': False, 'message': 'Error: ' + str(e)})


@form.route('/form/<id>', methods=['PUT'])
def update(id):
    try:
        requestData = request.get_json()
        print(requestData)
        res = FormsDataQueryService.update(id, requestData)
        return jsonify({'status': True, 'forms_data': res})
    except Exception as e:
        return jsonify({'status': False, 'message': 'Error: ' + str(e)})


@form.route('/form/schema/<name>', methods=['GET'])
def getFormsSchemaByName(name):
    try:
        res = FormsSchemaQueryService.getFormsSchemaByName(name)
        return jsonify({'status': True, 'forms_schema': res})
    except Exception as e:
        return jsonify({'status': False, 'message': str(e)})


# Get Absence Form By Approval Status Parameters API
# API example: localhost:8888/form/absence/approval?status=<status>
# function: getAbsenceFormByApprovalStatus
# input: status
# output: list of Absence Form Data
@form.route('/form/absence/approval', methods=['GET'])
def getAbsenceFormByApprovalStatus():
    try:
        status = request.args.get('status')
        print(status)
        res = DocumentsApprovalQueryService.getDocumentsApprovalWithFormsByStatusAndFormsSchemaName(
            status, '請假表')
        return jsonify({'status': True, 'absences_form': res})
    except Exception as e:
        return jsonify({'status': False, 'message': str(e)})


@form.route('/form/absence/approval/<id>', methods=['GET'])
def getAbsenceFormByApprovalID(id):
    try:
        res = DocumentsApprovalQueryService.getDocumentsApprovalWithFormsByIDAndFormsSchemaName(
            id, '請假表')
        return jsonify({'status': True, 'absences_form': res})
    except Exception as e:
        return jsonify({'status': False, 'message': str(e)})


@form.route('/form/absence/<id>/approval', methods=['PUT'])
def updateAbsenceFormApprovalStatus(id):
    try:
        status = request.args.get('status')
        res = DocumentsApprovalQueryService.update(id, {'status': status})
        return jsonify({'status': True, 'documents_approval': res})
    except Exception as e:
        return jsonify({'status': False, 'message': str(e)})
