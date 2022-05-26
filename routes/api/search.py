from crypt import methods
import json
from flask import Blueprint, jsonify, request, render_template, send_from_directory
from services.database import DatabaseService

search = Blueprint('search', __name__)


@search.route('/search/content', methods=['GET'])
def searchDocumentByContent():
    res = DatabaseService.searchDocumentByContent(request.args.get('content'))
    return jsonify({'documents': res})


@search.route('/search/name', methods=['GET'])
def searchDocumentByName():
    res = DatabaseService.searchDocumentByName(request.args.get('name'))
    return jsonify({'documents': res})


@search.route('/count/document/<date>', methods=['GET'])
def countEachLabelDocumentByDate(date):
    res = DatabaseService.countEachLabelDocumentByDate(date)
    return jsonify({'documents': res})

@search.route('/search/form/<date>', methods=['GET'])
def searchFormByDate(date):
    res = DatabaseService.getFormDataByDate(date)
    return jsonify({'forms': res})

@search.route('/search/form/<label>/<date>', methods=['GET'])
def searchFormByLabelAndDate(date, label):
    res = DatabaseService.searchFormByLabelAndDate(label, date)
    return jsonify({'forms': res})