from crypt import methods
import json
from flask import Blueprint, jsonify, request, render_template, send_from_directory
from services.database import DatabaseService

label = Blueprint('label', __name__)


@label.route('/labels', methods=['GET'])
def labels():
    res = DatabaseService.getAllLabel()
    return jsonify({'prediction': res})


@label.route('/labels', methods=['POST'])
def new():
    print(request.form.get('name'))
    res = DatabaseService.addNewLabel(request.form.get('name'))
    return jsonify({'prediction': str(res)})
