from database.models.Documents import Documents
from database.models.FormsData import FormsData
from database.services.Documents import DocumentsQueryService
from database.services.FormsData import FormsDataQueryService
from flask import Blueprint, jsonify, request, render_template, send_from_directory
from services.database import DatabaseService
from utils.model import rowsKeyFromSingleQuotation2doubleQuotation
from sqlalchemy import cast, DATE

search = Blueprint('search', __name__)


@search.route('/search/content', methods=['GET'])
def searchDocumentByContent():
    content = request.args.get('content')
    res = DocumentsQueryService.getDocumentsByContent(content)
    return jsonify({'documents': res})


@search.route('/search/name', methods=['GET'])
def searchDocumentByName():
    name = request.args.get('name')
    res = DocumentsQueryService.getDocumentByName(name)
    return jsonify({'documents': res})


@search.route('/search/form/<date>', methods=['GET'])
def searchFormByDate(date):
    res = FormsDataQueryService.getFormsByDate(date)
    return jsonify({'forms': res})


@search.route('/search/form/<label>/<date>', methods=['GET'])
def searchFormByLabelAndDate(label, date):
    try:
        res = FormsDataQueryService.getFormsByLabelAndDate(label, date)
        return jsonify({'status': True, 'form_schema': res[0], 'form_data': res[1]})
    except Exception as e:
        print(e)
        return jsonify({'status': False, 'message': 'No form found'})
