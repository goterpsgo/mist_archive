from flask import Blueprint, jsonify, request, render_template, current_app
import config
import json

index_routes = Blueprint('index_routes', __name__)

@index_routes.route('/')
@index_routes.route('/index')
def index():
    _params = {
          "title": "MIST!"
        , "greeting": "Today is Monday."
    }
    return render_template("index.html", params = _params)

    # return "Hello world!!!"
    # return current_app.config["CSRF_SESSION_KEY"]
