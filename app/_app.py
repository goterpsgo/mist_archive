# currently not used; retained as reference - JWT 16 Aug 2016
from flask import Flask, Blueprint, render_template, session, redirect, url_for, escape, request, abort

app = Flask(__name__)
app.config.from_pyfile("./config.py")

def return_app():
  return app
