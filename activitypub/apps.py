from django.apps import AppConfig
from flask import Flask

class ActivitypubConfig(AppConfig):
    name = 'activitypub'

def create_app():
    app = Flask(__name__, static_folder='../media')
    return app

app = create_app()

@app.route('/')
def index():
    return "THIS IS FLASK INDEX PAGE."

import activitypub.api
import webfinger
