from crypt import methods
import json
import os

from flask import Blueprint, jsonify, request, render_template, send_from_directory
from services.classification import ClassificationService
from services.ocr import OCRService
from services.storage import StorageService
from werkzeug.utils import secure_filename

storage = Blueprint('storage', __name__)

ALLOWED_EXTENSIONS = set(['pdf', 'png', 'jpg', 'jpeg'])

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@storage.route('/upload', methods=['POST'])
def upload():
    files = request.files.getlist('document[]')
    for file in files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            document = StorageService.upload(file, filename)
    return jsonify({'status': 'uploaded'})
