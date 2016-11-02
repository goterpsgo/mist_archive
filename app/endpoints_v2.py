from flask import Blueprint, jsonify, request, render_template, current_app, make_response
from flask_restful import Resource, Api, reqparse, abort
from flask_jwt import JWT, jwt_required, current_identity
from mist_main import return_app
from sqlalchemy.orm import scoped_session
from common.models import main, base_model
import hashlib
import re
import config
import json
import requests
import socket

api_endpoints = Blueprint('mist_auth', __name__, url_prefix="/api/v2")
api = Api(api_endpoints)
this_app = return_app()


def rs_users():
    return main.session.query(main.MistUser).join(main.UserPermission, main.MistUser.permission_id == main.UserPermission.id)


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
    user = main.session.query(main.MistUser)\
      .filter(main.MistUser.username==username, main.MistUser.password==hashlib.sha256(password).hexdigest())\
      .first()
    users = main.session.query()
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
    # 'SECRET_KEY' is used to decode and validate token
    decoded_token = jwt.jwt_decode_callback(incoming_token)

    # create _Identity instance for use with flask_jwt.jwt_encode_callback()
    obj_identity = _Identity(decoded_token["identity"])
    return jwt.jwt_encode_callback(obj_identity)


def create_user_dict(obj_user):
    user = {
          'id': obj_user.id
        , 'username': obj_user.username
        , 'permission_id': obj_user.permission_id
        , 'subject_dn': obj_user.subjectDN
        , 'first_name': obj_user.firstName
        , 'last_name': obj_user.lastName
        , 'organization': obj_user.organization
        , 'lockout': obj_user.lockout
        , 'permission': obj_user.permission.name
    }
    return user


class TodoItem(Resource):
    def get(self, id):
        return {'task': 'Say "Hello, World!!!"'}


class SecureMe(Resource):
    @jwt_required()
    def get(self, id):
        return {'message': 'You are looking at /secureme: ' + str(id)}


class Users(Resource):
    @jwt_required()
    def get(self, _user=None):
        rs_dict = dict()    # used to hold and eventually return users_list[] recordset and associated metadata
        rs_dict['Authorization'] = create_new_token(request)   # pass token via response data since I can't figure out how to pass it via response header - JWT Oct 2016

        # query for user/users
        rs_users_handle = rs_users()
        r_single_user = None
        if _user is not None:
            if re.match('^[0-9]+$', _user):
                r_single_user = rs_users_handle.filter(main.MistUser.id == int(_user)).first()  # use int value for .id
            else:
                r_single_user = rs_users_handle.filter(main.MistUser.username == _user).first() # use str value for .username

        # add results to users_list[]
        users_list = []
        if _user is None:
            for r_user in rs_users():
                users_list.append(create_user_dict(r_user))
        else:
            users_list.append(create_user_dict(r_single_user))
        rs_dict['users_list'] = users_list  # add users_list[] to rs_dict

        return jsonify(rs_dict) # return rs_dict

    def post(self):
        form_fields = request.get_json(force=True)

        new_user = main.MistUser(
              username = form_fields['username']
            , password = form_fields['password']
            # , permission = main.UserPermission(id=2)  # adds new value to userPermissions table
            , permission = main.session.query(main.UserPermission).filter(main.UserPermission.name == 'Normal User').first()
            , subjectDN = form_fields['subject_dn']
            , firstName = form_fields['first_name']
            , lastName = form_fields['last_name']
            , organization = form_fields['organization']
            , lockout = "No"
            , permission_id = 2
        )
        main.session.add(new_user)
        main.session.commit()
        main.session.flush()

        return {'response': {'id': new_user.id}}

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
api.add_resource(Logout, '/logout')
api.add_resource(Users, '/users', '/user/<string:_user>')
api.add_resource(AddUser, '/adduser')
api.add_resource(UpdateUser, '/updateuser/<int:id>')
api.add_resource(DisableUser, '/disableuser/<int:id>')
api.add_resource(DeleteUser, '/deleteuser/<int:id>')
