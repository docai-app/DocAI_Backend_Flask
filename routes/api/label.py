import os
from database.models.Labels import Labels
from database.services.Labels import LabelsQueryService
from flask import Blueprint, jsonify, request
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
label = Blueprint('label', __name__)


@label.route('/labels', methods=['GET'])
def labels():
    res = LabelsQueryService.getAll()
    return jsonify({'labels': res})


@label.route('/labels', methods=['POST'])
def new():
    requestData = request.get_json()
    name = requestData['name']
    res = LabelsQueryService.insert(name)
    return jsonify({'status': res})


# Update specify label's name API
@label.route('/labels/<id>', methods=['PUT'])
def update(id):
    try:
        requestData = request.get_json()
        name = requestData['name']
        res = LabelsQueryService.update(id, name)
        return jsonify({'status': res})
    except Exception as e:
        return jsonify({'status': res, 'message': 'No label found'})
