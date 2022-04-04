from crypt import methods
import json
from flask import Blueprint, jsonify, request, render_template, send_from_directory
from services.database import DatabaseService

search = Blueprint('search', __name__)


@search.route('/search/content', methods=['GET'])
def searchDocumentByContent():
    res = DatabaseService.searchDocumentByContent(request.args.get('content'))
    return jsonify({'prediction': res})

@search.route('/search/name', methods=['GET'])
def searchDocumentByName():
    res = DatabaseService.searchDocumentByName(request.args.get('name'))
    return jsonify({'prediction': res})


@search.route('/search', methods=['POST'])
def new():
    name = request.form.get('name')
    res = DatabaseService.addNewLabel(name)
    return jsonify({'prediction': str(res)})

@search.route('/count/document/<date>', methods=['GET'])
def countEachLabelDocumentByDate(date):
    res = DatabaseService.countEachLabelDocumentByDate(date)
    return jsonify({'prediction': res})