from crypt import methods
import json
from database.models.Documents import Documents
from database.models.FormsData import FormsData
from flask import Blueprint, jsonify, request, render_template, send_from_directory
from services.database import DatabaseService
from utils.model import row2dict, rows2dict
from sqlalchemy import cast, DATE

search = Blueprint('search', __name__)


@search.route('/search/content', methods=['GET'])
def searchDocumentByContent():
    content = request.args.get('content')
    data = Documents.query.filter(
        Documents.content.like('%' + content + '%')).all()
    res = rows2dict(data)
    return jsonify({'documents': res})


@search.route('/search/name', methods=['GET'])
def searchDocumentByName():
    name = request.args.get('name')
    data = Documents.query.filter(Documents.name.like('%' + name + '%')).all()
    res = rows2dict(data)
    return jsonify({'documents': res})


@search.route('/count/document/<date>', methods=['GET'])
def countEachLabelDocumentByDate(date):
    data = DatabaseService.countEachLabelDocumentByDate(date)
    print(data)
    return jsonify({'documents': data})


@search.route('/search/form/<date>', methods=['GET'])
def searchFormByDate(date):
    data = FormsData.query.filter(cast(FormsData.created_at, DATE) == date).all()
    res = rows2dict(data)
    return jsonify({'forms': res})


@search.route('/search/form/<label>/<date>', methods=['GET'])
def searchFormByLabelAndDate(date, label):
    res = DatabaseService.searchFormByLabelAndDate(label, date)
    return jsonify({'forms': res})
