from database.models.Roles import Roles
from database.models.DocumentsApproval import DocumentsApproval
from database.models.DocumentFolder import DocumentFolder
from database.models.Folders import Folders
from database.models.FormsData import FormsData
from database.models.FormsSchema import FormsSchema
from database.models.Documents import Documents
from database.models.Labels import Labels
from database.models.Users import Users
import os
from flask import Flask
from flask_migrate import Migrate
from ext import db
from routes.api.classification import classification
from routes.api.label import label
from routes.api.storage import storage
from routes.api.search import search
from routes.api.form import form
from routes.api.document import document
from routes.api.statistics import statistics
from flask_cors import CORS
from dotenv import load_dotenv
load_dotenv()


os.environ['TZ'] = 'Asia/Taipei'


def createApp(config="database/settings.py"):
    app = Flask(__name__)
    app.config.from_pyfile(config)
    app.config['TIMEZONE'] = 'Asia/Taipei'
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.register_blueprint(classification)
    app.register_blueprint(storage)
    app.register_blueprint(label)
    app.register_blueprint(search)
    app.register_blueprint(form)
    app.register_blueprint(document)
    app.register_blueprint(statistics)
    CORS(app, resources={
         r"/*": {"origins": ["*", "https://doc-ai-frontend-oqag5r4lf-chonwai.vercel.app/", "https://doc-ai-frontend.vercel.app/"]}})

    db.init_app(app)
    migrate = Migrate(app, db, compare_type=True)
    migrate.init_app(app, db)
    return app


app = createApp()


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8888)
