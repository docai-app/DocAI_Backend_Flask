from crypt import methods
import uuid
from database.models.Labels import Labels
from flask import Blueprint, jsonify, request, render_template, send_from_directory
from services.database import DatabaseService
from utils.model import row2dict, rows2dict
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
label = Blueprint('label', __name__)


@label.route('/labels', methods=['GET'])
def labels():
    # data = Labels.query.all()
    # res = rows2dict(data)
    data = Labels.query.first()
    # res = row2dict(data)
    print(data)
    return jsonify({'labels': data})


@label.route('/labels', methods=['POST'])
def new():
    name = request.form.get('name')
    label = Labels(str(uuid.uuid4()), name)
    db.session.add(label)
    db.session.commit()
    return jsonify({'status': 'Added', 'label': row2dict(label)})
