from flask import Blueprint, jsonify, request, render_template, current_app, make_response
from flask_restful import Resource, Api, reqparse, abort
from flask_jwt import JWT, jwt_required, current_identity
from werkzeug.security import safe_str_cmp
from mist_main import return_app
from sqlalchemy.orm import sessionmaker, scoped_session
from common.models import main, base_model
import hashlib
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


# NOTE: only used with flask_jwt.jwt_encode_callback()
class _Identity():
    def __init__(self, id):
        self.id = id

# Create and return new JWT token
# Extracts "id" value from previous token embedded in request header and uses it to build new token
def create_new_token(request):
    # incoming_token provided by $httpProvider.interceptor from the browser request
    incoming_token = request.headers.get('authorization').split()[1]

    # value of this_app.config['SECRET_KEY'] is implicitly provided to flask_jwt.jwt_decode_callback()
    decoded_token = jwt.jwt_decode_callback(incoming_token)

    # create _Identity instance for use with flask_jwt.jwt_encode_callback()
    obj_identity = _Identity(decoded_token["identity"])
    return "JWT %s" % jwt.jwt_encode_callback(obj_identity)


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
        return jsonify(users), 201, {'Authorization': create_new_token(request)}    # TODO: will need to test this mechanism - JWT 14 Oct 2016


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
            return user, 201, {'Authorization': create_new_token(request)}
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
            return user, 201, {'Authorization': create_new_token(request)}
        else:
            return {"message": "No such user."}


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
api.add_resource(AddUser, '/adduser')
api.add_resource(UpdateUser, '/updateuser/<int:id>')
api.add_resource(DisableUser, '/disableuser/<int:id>')
api.add_resource(DeleteUser, '/deleteuser/<int:id>')
api.add_resource(Users, '/users')
api.add_resource(UserById, '/userbyid/<int:id>')
api.add_resource(UserByUsername, '/userbyusername/<string:username>')
