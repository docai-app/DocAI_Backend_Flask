import os
from flask import Flask, render_template, Response
from flask import g
import numpy as np
import threading
from time import sleep
from config.cacha import config
from routes.api.classification import classification
from routes.api.label import label
from routes.api.storage import storage
from routes.api.search import search
from routes.api.form import form
from flask_cors import CORS


os.environ['TZ'] = 'Asia/Taipei'

DATABASE = './database/database.db'

app = Flask(__name__)
app.config.from_mapping(config)
app.register_blueprint(classification)
app.register_blueprint(storage)
app.register_blueprint(label)
app.register_blueprint(search)
app.register_blueprint(form)
CORS(app, resources={r"/*": {"origins": ["*", "https://doc-ai-frontend-oqag5r4lf-chonwai.vercel.app/", "https://doc-ai-frontend.vercel.app/"]}})


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


@app.route('/')
def index():
    """Video streaming home page."""
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8888)
