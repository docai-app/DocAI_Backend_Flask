from database.services.FormsData import FormsDataQueryService
from database.services.FormSchemas import FormSchemasQueryService
from flask import Blueprint, jsonify, request
from services.AzureForm import AzureFormService
from services.form import FormService
import os

form_recognize = Blueprint('form_recognize', __name__)

model_id = os.getenv("AZURE_ABSENCE_FORM_MODEL_ID")


@form_recognize.route('/alpha/form/recognize/absence', methods=['POST'])
def form_recognize_absence():
    try:
        form_url = request.form.get('document_url')
        res = AzureFormService.analysisForm(model_id, form_url)
        absenceFormData = FormService.mapAbsenceForm(res)
        return jsonify({'status': True, 'form_url': form_url, 'absence_form_data': absenceFormData, 'form': res})
    except Exception as e:
        print(e)
        return jsonify({'status': False, 'message': 'Error: ' + str(e)})


@form_recognize.route('/alpha/form/recognize', methods=['POST'])
def form_recognize_specific():
    try:
        form_url = request.form.get('document_url')
        model_id = request.form.get('model_id')
        res = AzureFormService.analysisForm(model_id, form_url)
        recognizeFormData = FormService.mapForm(res, model_id)
        return jsonify({'status': True, 'form_url': form_url, 'recognized_form_data': recognizeFormData, 'form': res})
    except Exception as e:
        print(e)
        return jsonify({'status': False, 'message': 'Error: ' + str(e)})
