
from flask import Blueprint, jsonify, request, render_template, current_app, make_response
from flask_restful import Resource, Api, reqparse, abort
from flask_jwt import JWT, jwt_required, current_identity
from werkzeug.security import safe_str_cmp
from _app import return_app
from sqlalchemy.orm import sessionmaker
from common.models import main, base_model
import hashlib
# import jwt
import config
import json
import requests
import socket

api_auth = Blueprint('mist_auth', __name__, url_prefix="/auth_api")
api = Api(api_auth)
this_app = return_app()

parser = reqparse.RequestParser()

# DBSession = sessionmaker()
# DBSession.bind = main.engine
DBSession = sessionmaker(bind=main.engine)
session = DBSession()

class User(object):
  def __init__(self, id, username, password):
    self.id = id
    self.username = username
    self.password = password

  def __str__(self):
    return "User(id='%s')" % self.id


users = [
  User(1, 'user1', 'abcxyz'),
  User(2, 'user2', 'abcxyz'),
]


# dictionary comprehensions
# using the for loop to create a dictionary with "u.username: u" pairs
# NOTE: dictionary comprehensions not used prior to Python v2.7
username_table = {u.username: u for u in users}
userid_table = {u.id: u for u in users}
#
# # username_table = dict((u.username, u) for (User.username, u) in users)
# # userid_table = dict((u.id, u) for (User.id, u) in users)
# username_table = {'user1': users[0], 'user2': users[1]}
# userid_table = {1: users[0], 2: users[1]}


def authenticate(username, password):
  user = session.query(main.MistUsers)\
      .filter(main.MistUsers.username==username, main.MistUsers.password==hashlib.sha256(password).hexdigest())\
      .first()
  if hasattr(user, 'username'):
      return user



  # user = username_table.get(username, None)
  # if user and safe_str_cmp(user.password.encode('utf-8'), password.encode('utf-8')):
  #   return user


def identity(payload):
  user_id = payload['identity']
  return userid_table.get(user_id, None)


jwt = JWT(this_app, authenticate, identity)


# @current_app.route('/protected')
# @jwt_required()
# def protected():
#   return '%s' % current_identity










class TodoItem(Resource):
    def get(self, id):
        return {'task': 'Say "Hello, World!!!"'}

class Login(Resource):
    jwt = JWT(this_app, authenticate, identity)
    def post(self):
        # print current_identity
        # print("======================================================================")

        if request.data:
            # print("[jwt] %", dir(jwt))
            # print("======================================================================")
            # print("[jwt] %", vars(jwt))

            # print(request.data)
            # form_data = json.loads(request.data)
            # print("[92] data: " + request.data)
            # url = "http://10.11.1.239:8080/auth"
            # print("[94] url: " + url)
            # print ("[95] data: " + request.data)
            # # resp = requests.post("http://10.11.1.239:8080/auth", data={'username':'user1', 'password': 'abcxyz'})
            # # resp = requests.post(url, data=request.data, headers={"Content-Type": "application/json"})
            # # print("[97] Got here")
            # # print(dir(resp))
            # # print("[96] content: " + resp.content)
            # # POST data is saved as dict key value, can't figure out why - JWT 28 Jul 2016
            # # (k, v), = request.get_json().to_dict().items()
            # # d = json.loads(k)
            # # print("d: %s" % d["username"])
            # # foo = authenticate(d["username"], d["password"])
            # # print("foo: %s" % foo)
            # #
            # # # jwt = JWT(this_app, authenticate, identity)
            # # print ("jwt: %s" % jwt.identity_callback)
            # #
            # #
            # #
            # # resp = make_response()
            # # # token = jwt.encode
            # # # print token
            # # # resp.headers["foo"] = "bar"
            # # # print resp.headers
            # # # print current_app.config["JWT_VERIFY_CLAIMS"]
            # # # return resp
            # # print current_app
            return {'token': 'Got here'}
        else:
            return {'token': 'no form data'}

    def get(self):
        return {'message': 'No GET method for this endpoint.'}

class Signup(Resource):
    def post(self):
        args = parser.parse_args()
        return {'response': 'I signed up!!!'}
    def get(self):
        return {'message': 'No GET method for this endpoint.'}

class Logout(Resource):
    def post(self):
        args = parser.parse_args()
        return {'response': 'I''m logged out!!!'}
    def get(self):
        return {'message': 'No GET method for this endpoint.'}

class Validate(Resource):
    @jwt_required()
    def post(self):
        args = parser.parse_args()

        # def protected():
        #   return '%s' % current_identity
        return {'token': 'token_stub'}
    def get(self):
        print ('%s' % current_identity)
        return {'message': 'No GET method for this endpoint.'}

class AddUser(Resource):
    def post(self):
        args = parser.parse_args()
        return {'response': 'Created new user!!!'}
    def get(self):
        return {'message': 'No GET method for this endpoint.'}

class UpdateUser(Resource):
    def post(self):
        args = parser.parse_args()
        return {'response': 'Created new user!!!'}
    def get(self, id):
        return {'message': 'No GET method for this endpoint.'}

class DisableUser(Resource):
    def post(self):
        args = parser.parse_args()
        return {'response': 'Created new user!!!'}
    def get(self, id):
        return {'message': 'No GET method for this endpoint.'}

class DeleteUser(Resource):
    def post(self):
        args = parser.parse_args()
        return {'response': 'Created new user!!!'}
    def get(self, id):
        return {'message': 'No GET method for this endpoint.'}

class Users(Resource):
    def get(self):
        return {'result': 'Users list endpoint.'}

class User(Resource):
    def get(self, id):
        return {'result': 'User details endpoint.'}

api.add_resource(TodoItem, '/todos/<int:id>')
api.add_resource(Login, '/login')
api.add_resource(Signup, '/signup')
api.add_resource(Logout, '/logout')
api.add_resource(Validate, '/validate')
api.add_resource(AddUser, '/adduser')
api.add_resource(UpdateUser, '/updateuser/<int:id>')
api.add_resource(DisableUser, '/disableuser/<int:id>')
api.add_resource(DeleteUser, '/deleteuser/<int:id>')
api.add_resource(Users, '/users')
api.add_resource(User, '/user/<int:id>')
