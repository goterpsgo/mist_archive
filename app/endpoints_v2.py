from flask import Blueprint, jsonify, request, render_template, current_app, make_response
from flask_restful import Resource, Api, reqparse, abort
from flask_jwt import JWT, jwt_required, current_identity
from werkzeug.security import safe_str_cmp
from mist_main import return_app
from sqlalchemy.orm import sessionmaker, scoped_session
from common.models import main, base_model
import hashlib
# import jwt
import config
import json
import requests
import socket

api_endpoints = Blueprint('mist_auth', __name__, url_prefix="/api/v2")
api = Api(api_endpoints)
this_app = return_app()

parser = reqparse.RequestParser()

# DBSession = sessionmaker()
# DBSession.bind = main.engine
DBSession = scoped_session(sessionmaker(bind=main.engine))
session = DBSession()

def rs_users():
    return session.query(main.MistUser).join(main.UserPermission, main.MistUser.permission_id == main.UserPermission.id)

# TODO: refactor authenticate() into User class if possible
class User(object):
    # def __init__(self, id, username, password):
    def __init__(self, **kwargs):
        self.id = kwargs['id']
        # self.username = kwargs['username']
        # self.password = kwargs['password']
        # self.username = username
        # self.password = password

    def get(self):
        r_user = rs_users().filter(main.MistUser.id == self.id).first()
        if hasattr(r_user, 'username'):
            user = {
                  'id': r_user.id
                , 'username': r_user.username
                , 'permission_id': r_user.permission_id
                , 'subject_dn': r_user.subjectDN
                , 'first_name': r_user.firstName
                , 'last_name': r_user.lastName
                , 'organization': r_user.organization
                , 'lockout': r_user.lockout
                , 'permission': r_user.permission.name
            }
            return jsonify(user)
        else:
            return {"message": "No such user."}

    # def __str__(self):
    #     return "User(id='%s')" % self.id

def authenticate(username, password):
    user = session.query(main.MistUser)\
      .filter(main.MistUser.username==username, main.MistUser.password==hashlib.sha256(password).hexdigest())\
      .first()
    users = session.query()
    if hasattr(user, 'username'):
      return user

def identity(payload):
    user_id = payload['identity']
    return User(id=user_id).get()

jwt = JWT(this_app, authenticate, identity)

class TodoItem(Resource):
    def get(self, id):
        return {'task': 'Say "Hello, World!!!"'}

class SecureMe(Resource):
    @jwt_required()
    def get(self, id):
        return {'message': 'You are looking at /secureme: ' + str(id)}

class Users(Resource):
    @jwt_required()
    def get(self):
        # rs_users = session.query(main.MistUser).join(main.UserPermission, main.MistUser.permission_id == main.UserPermission.id)
        users = []
        for r_user in rs_users():
            user = {
                  'id': r_user.id
                , 'username': r_user.username
                , 'permission_id': r_user.permission_id
                , 'subject_dn': r_user.subjectDN
                , 'first_name': r_user.firstName
                , 'last_name': r_user.lastName
                , 'organization': r_user.organization
                , 'lockout': r_user.lockout
                , 'permission': r_user.permission.name
            }
            users.append(user)
        return jsonify(users)

class UserById(Resource):
    @jwt_required()
    def get(self, id):
        r_user = rs_users().filter(main.MistUser.id == id).first()
        if hasattr(r_user, 'username'):
            user = {
                  'id': r_user.id
                , 'username': r_user.username
                , 'permission_id': r_user.permission_id
                , 'subject_dn': r_user.subjectDN
                , 'first_name': r_user.firstName
                , 'last_name': r_user.lastName
                , 'organization': r_user.organization
                , 'lockout': r_user.lockout
                , 'permission': r_user.permission.name
            }
            return jsonify(user)
        else:
            return {"message": "No such user."}

class UserByUsername(Resource):
    @jwt_required()
    def get(self, username):
        r_user = rs_users().filter(main.MistUser.username == username).first()
        if hasattr(r_user, 'username'):
            user = {
                  'id': r_user.id
                , 'username': r_user.username
                , 'permission_id': r_user.permission_id
                , 'subject_dn': r_user.subjectDN
                , 'first_name': r_user.firstName
                , 'last_name': r_user.lastName
                , 'organization': r_user.organization
                , 'lockout': r_user.lockout
                , 'permission': r_user.permission.name
            }
            return jsonify(user)
        else:
            return {"message": "No such user."}


# class Login(Resource):
#     jwt = JWT(this_app, authenticate, identity)
#     def post(self):
#         # print current_identity
#         # print("======================================================================")
#
#         if request.data:
#             # print("[jwt] %", dir(jwt))
#             # print("======================================================================")
#             # print("[jwt] %", vars(jwt))
#
#             # print(request.data)
#             # form_data = json.loads(request.data)
#             # print("[92] data: " + request.data)
#             # url = "http://10.11.1.239:8080/auth"
#             # print("[94] url: " + url)
#             # print ("[95] data: " + request.data)
#             # # resp = requests.post("http://10.11.1.239:8080/auth", data={'username':'user1', 'password': 'abcxyz'})
#             # # resp = requests.post(url, data=request.data, headers={"Content-Type": "application/json"})
#             # # print("[97] Got here")
#             # # print(dir(resp))
#             # # print("[96] content: " + resp.content)
#             # # POST data is saved as dict key value, can't figure out why - JWT 28 Jul 2016
#             # # (k, v), = request.get_json().to_dict().items()
#             # # d = json.loads(k)
#             # # print("d: %s" % d["username"])
#             # # foo = authenticate(d["username"], d["password"])
#             # # print("foo: %s" % foo)
#             # #
#             # # # jwt = JWT(this_app, authenticate, identity)
#             # # print ("jwt: %s" % jwt.identity_callback)
#             # #
#             # #
#             # #
#             # # resp = make_response()
#             # # # token = jwt.encode
#             # # # print token
#             # # # resp.headers["foo"] = "bar"
#             # # # print resp.headers
#             # # # print current_app.config["JWT_VERIFY_CLAIMS"]
#             # # # return resp
#             # # print current_app
#             return {'token': 'Got here'}
#         else:
#             return {'token': 'no form data'}
#
#     def get(self):
#         return {'message': 'No GET method for this endpoint.'}

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

api.add_resource(TodoItem, '/todos/<int:id>')
api.add_resource(SecureMe, '/secureme/<int:id>')
api.add_resource(Signup, '/signup')
api.add_resource(Logout, '/logout')
api.add_resource(Validate, '/validate')
api.add_resource(AddUser, '/adduser')
api.add_resource(UpdateUser, '/updateuser/<int:id>')
api.add_resource(DisableUser, '/disableuser/<int:id>')
api.add_resource(DeleteUser, '/deleteuser/<int:id>')
api.add_resource(Users, '/users')
api.add_resource(UserById, '/userbyid/<int:id>')
api.add_resource(UserByUsername, '/userbyusername/<string:username>')
