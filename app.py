from dataclasses import dataclass
import os
from flask import Flask, render_template, Response
from flask_migrate import Migrate
from ext import db
from routes.api.classification import classification
from routes.api.label import label
from routes.api.storage import storage
from routes.api.search import search
from routes.api.form import form
from flask_cors import CORS


os.environ['TZ'] = 'Asia/Taipei'


def createApp(config="settings.py"):
    app = Flask(__name__)
    app.config.from_pyfile(config)
    app.register_blueprint(classification)
    app.register_blueprint(storage)
    app.register_blueprint(label)
    app.register_blueprint(search)
    app.register_blueprint(form)
    CORS(app, resources={
         r"/*": {"origins": ["*", "https://doc-ai-frontend-oqag5r4lf-chonwai.vercel.app/", "https://doc-ai-frontend.vercel.app/"]}})
    return app


app = createApp()
db.init_app(app)
migrate = Migrate(app, db)


from database.models.Users import Users
from database.models.Labels import Labels
from database.models.Documents import Documents
from database.models.FormsSchema import FormsSchema
from database.models.FormsData import FormsData
from database.models.Folders import Folders
from database.models.DocumentFolder import DocumentFolder
from database.models.DocumentsApproval import DocumentsApproval


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8888)
