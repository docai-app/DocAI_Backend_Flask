# import eventlet
from routes.api.autogen import assistant_core
import json
from database.services.AutogenAgents import AutogenAgentService
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
from flask import Flask, got_request_exception, request, jsonify
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
from routes.api.autogen import autogen_api
from routes.api.smart_extraction_schema import smart_extraction_schema
from flask_cors import CORS
from flask_socketio import SocketIO, emit
from ddtrace import tracer
from dotenv import load_dotenv

load_dotenv()


os.environ["TZ"] = "Asia/Taipei"

tracer.configure(
    hostname="datadog-agent-dev",
    port=8126,
)

# eventlet.monkey_patch()


def createApp(config="database/settings.py"):
    app = Flask(__name__)
    app.config.from_pyfile(config)
    app.config["TIMEZONE"] = "Asia/Taipei"
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
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
    app.register_blueprint(autogen_api)
    CORS(
        app,
        resources={
            r"/*": {
                "origins": [
                    "*",
                    "http://localhost:3000",
                    "https://test-docai-chatbot-plus.vercel.app",
                    "https://doc-ai-frontend-oqag5r4lf-chonwai.vercel.app/",
                    "https://doc-ai-frontend.vercel.app/",
                    "https://chatbot-demo.docai.net",
                    "http://chatbot-demo.docai.net",
                    "https://prod-docai-chatbot.vercel.app",
                    "http://prod-docai-chatbot.vercel.app",
                    "https://dev-docai-chatbot.vercel.app",
                    "http://dev-docai-chatbot.vercel.app",
                    "https://docai-chatbot-next.vercel.app",
                    "http://docai-chatbot-next.vercel.app",
                    "https://dev-docai-chatbot-plus.vercel.app",
                    "http://dev-docai-chatbot-plus.vercel.app/",
                    "https://test-docai-chatbot-plus.vercel.app",
                    "https://chyb-dev.docai.net",
                    "https://chyb.docai.net",
                    "http://chyb-dev.docai.net",
                    "http://chyb.docai.net",
                    "http://chatbot-dev.docai.net",
                    "https://chatbot-dev.docai.net",
                    "http://chatbot.docai.net",
                    "https://chatbot.docai.net"
                ]
            }
        },
    )
    db.init_app(app)
    migrate = Migrate(app, db, compare_type=True)
    migrate.init_app(app, db)

    return app


app = createApp()
# socketio = SocketIO(app, cors_allowed_origins="*",
#                     logger=True, engineio_logger=True)

socketio = SocketIO(
    app,
    ping_timeout=600, ping_interval=300,
    cors_allowed_origins=[
        "http://localhost:3000",
        "https://test-docai-chatbot-plus.vercel.app",
        "https://chyb-dev.docai.net",
        "https://chyb.docai.net",
        "http://chyb-dev.docai.net",
        "http://chyb.docai.net",
        "http://chatbot-dev.docai.net",
        "https://chatbot-dev.docai.net",
        "http://chatbot.docai.net",
        "https://chatbot.docai.net"
    ],
)


@app.before_first_request
def init_rollbar():
    """init rollbar module"""
    rollbar.init(
        # access token
        os.getenv("ROLLBAR_ACCESS_TOKEN"),
        # environment name
        "production",
        # server root directory, makes tracebacks prettier
        root=os.path.dirname(os.path.realpath(__file__)),
        # flask already sets up logging
        allow_logging_basic_config=False,
    )

    # send exceptions from `app` to rollbar, using flask's signal system.
    got_request_exception.connect(rollbar.contrib.flask.report_exception, app)


@app.route("/")
def hello():
    print("in hello")
    return "Hello World!"


@app.route("/test")
def test():
    agent = AutogenAgentService.get_assistant_agent_by_name("升學助手")
    return agent


# @app.route("/http-call")
# def http_call():
#     """return JSON with string data as the value"""
#     data = {'data': 'This text was fetched using an HTTP call to server on render'}
#     return jsonify(data)


@socketio.on('heartbeat')
def handle_heartbeat(message):
    # 可选：向客户端发送响应，确认心跳已接收
    emit('heartbeat_ack', {'data': 'Heartbeat received'})


@socketio.on('send_message')
def handle_message(data):
    print("Message received:", data)
    # emit('message', data, broadcast=True)
    # 只回傳給發送請求的客戶端
    # emit('message', json.loads(data), room=request.sid)

    json_data = json.loads(data)

    # call 我的 function
    assistant_core(json_data, {"emit": emit, "room": request.sid, "request": request})


if __name__ == "__main__":
    # app.run(debug=True, host='0.0.0.0', port=8888)
    socketio.run(app, debug=True, host="0.0.0.0", port=8888)
