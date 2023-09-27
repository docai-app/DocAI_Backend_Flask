from database.models.Roles import Roles
from database.models.DocumentsApproval import DocumentsApproval
from database.models.DocumentFolder import DocumentFolder
from database.models.Folders import Folders
from database.models.FormsData import FormsData
from database.models.FormSchemas import FormSchemas
from database.models.Documents import Documents
from database.models.Labels import Labels
from database.models.Users import Users
import os
import rollbar
import rollbar.contrib.flask
from flask import Flask, got_request_exception
from flask_migrate import Migrate
from ext import db
from routes.api.classification import classification
from routes.api.label import label
from routes.api.storage import storage
from routes.api.search import search
from routes.api.form import form
from routes.api.document import document
from routes.api.statistics import statistics
from routes.api.ocr import ocr
from routes.api.form_recognize import form_recognize
from routes.api.generate import generate
from routes.api.smart_extraction_schema import smart_extraction_schema
from flask_cors import CORS
from ddtrace import tracer
from dotenv import load_dotenv
load_dotenv()


os.environ['TZ'] = 'Asia/Taipei'

tracer.configure(
    hostname='datadog-agent-dev',
    port=8126,
)


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
    app.register_blueprint(ocr)
    app.register_blueprint(form_recognize)
    app.register_blueprint(generate)
    app.register_blueprint(smart_extraction_schema)
    CORS(app, resources={
         r"/*": {"origins": ["*", "https://doc-ai-frontend-oqag5r4lf-chonwai.vercel.app/", "https://doc-ai-frontend.vercel.app/"]}})
    db.init_app(app)
    migrate = Migrate(app, db, compare_type=True)
    migrate.init_app(app, db)

    return app


app = createApp()


@app.before_first_request
def init_rollbar():
    """init rollbar module"""
    rollbar.init(
        # access token
        os.getenv('ROLLBAR_ACCESS_TOKEN'),
        # environment name
        'production',
        # server root directory, makes tracebacks prettier
        root=os.path.dirname(os.path.realpath(__file__)),
        # flask already sets up logging
        allow_logging_basic_config=False)

    # send exceptions from `app` to rollbar, using flask's signal system.
    got_request_exception.connect(rollbar.contrib.flask.report_exception, app)


@app.route('/')
def hello():
    print("in hello")
    x = None
    x[5]
    return "Hello World!"


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8888)
