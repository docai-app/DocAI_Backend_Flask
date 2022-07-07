import os
from database.models.Labels import Labels
from database.services.Labels import LabelsQueryService
from flask import Blueprint, jsonify, request
from services.database import DatabaseService
from utils.model import row2dict, rows2dict
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
