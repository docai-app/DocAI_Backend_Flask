from crypt import methods
import json
import re
from flask import Blueprint, jsonify, request, render_template, send_from_directory
from services.database import DatabaseService

label = Blueprint('label', __name__)


@label.route('/labels', methods=['GET'])
def labels():
    res = DatabaseService.getAllLabel()
    return jsonify({'prediction': res})


@label.route('/labels', methods=['POST'])
def new():
    requestData = request.get_json()
    name = requestData['name']
    DatabaseService.addNewLabel(name)
    return jsonify({'status': 'Added'})
