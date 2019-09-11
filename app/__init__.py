from flask import Flask
from controller.property import app as property_controller

app = Flask(__name__)

app.register_blueprint(property_controller, url_prefix='/properties')