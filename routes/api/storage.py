from flask import Blueprint, jsonify, request
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
    return jsonify({'status': True})


@storage.route('/upload/bulk/label', methods=['POST'])
def uploadBulkWithSameLabel():
    files = request.files.getlist('document[]')
    label_id = request.form.get('label_id')
    for file in files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            document = StorageService.uploadBulkWithSameLabel(
                file, filename, label_id)
    return jsonify({'status': True})