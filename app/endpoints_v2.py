from flask import Blueprint, jsonify, request, render_template, current_app, make_response
from flask_restful import Resource, Api, reqparse, abort
from flask_jwt import JWT, jwt_required, current_identity
from mist_main import return_app
import sqlalchemy
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
                , 'permission': r_user.permissions.name
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
        , 'permission': obj_user.permissions.name
    }
    return user


class TodoItem(Resource):
    def get(self, id):
        return {'task': 'Say "Hello, World!!!"'}


class SecureMe(Resource):
    @jwt_required()
    def get(self, id):
        return {'message': 'You are looking at /secureme: ' + str(id)}


# Base class for handling MIST users
class Users(Resource):
    @jwt_required()
    # If get() gets a valid _user value (user ID or username), then the method will return a single user entry
    # If get() is not given a _user value, then the method will return a list of users
    def get(self, _user=None):
        try:
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

        except (main.Base.exc.NoResultFound) as e:
            {'response': {'message': e}}

    @jwt_required()
    # 1. Inserts new user into mistUsers table and returns user id
    # 2. Inserts repo and user association into userAccess table
    def post(self):
        # TODO: add error handler for handling inserting existing username values
        form_fields = request.get_json(force=True)

        new_user = main.MistUser(
              username=form_fields['username']
            , password=form_fields['password']
            , subjectDN=form_fields['subject_dn']
            , firstName=form_fields['first_name']
            , lastName=form_fields['last_name']
            , organization=form_fields['organization']
            , lockout="No"
            , permission_id=2
        )
        # main.session.rollback()
        main.session.add(new_user)
        main.session.commit()
        main.session.flush()

        for user_repo in form_fields['repos']:
            new_user_access = main.UserAccess(
                  repoID = user_repo['repo_id']
                , scID = user_repo['sc_id']
                , userID = new_user.id
                , userName = form_fields['username']
            )
            main.session.add(new_user_access)
            main.session.commit()
            main.session.flush()

        return {'response': {'user inserted': int(new_user.id)}}

    @jwt_required()
    # for a given user ID:
    # 1. Update simple fields directly into mistUsers table
    # 2. Extract user ID, username, delete all userAccess rows with that user ID, and insert new rows with user ID, username, scID, and repoID
    # 3. Update permission in mistUsers table
    def put(self, _user):
        form_fields = request.get_json(force=True)

        # Extract only simple fields (ie not permission, repos) and copy them into db_fields
        db_fields = {}
        for key, value in form_fields.iteritems():
            if (key != "repos"):
                db_fields[key] = value

        # Pass _user value to get mistUser object and update with values in db_fields
        main.session.query(main.MistUser).filter(main.MistUser.id == int(_user)).update(db_fields)
        db_fields = None

        # Delete entries in userAccess that have userID = _user
        main.session.query(main.UserAccess).filter(main.UserAccess.userID == int(_user)).delete()

        # Extract mistUser info and save into user
        rs_user_access = rs_users().filter(main.MistUser.id == int(_user)).first()
        user = create_user_dict(rs_user_access)

        for user_repo in form_fields['repos']:
            upd_user_access = main.UserAccess(
                  repoID = user_repo['repo_id']
                , scID = user_repo['sc_id']
                , userID = int(_user)
                , userName = user['username']
            )
            main.session.add(upd_user_access)
            main.session.commit()
            main.session.flush()

        return {'response': {'user updated': int(_user)}}

    @jwt_required()
    # removes user and their affiliated repos
    def delete(self, _user):
        if re.match('^[0-9]+$', _user):
            # use int value for .id
            main.session.query(main.UserAccess).filter(main.UserAccess.userID == int(_user)).delete()
            main.session.query(main.MistUser).filter(main.MistUser.id == int(_user)).delete()
        else:
            # use str value for .username
            main.session.query(main.UserAccess).filter(main.UserAccess.userName == _user).delete()
            main.session.query(main.MistUser).filter(main.MistUser.username == _user).delete()
        main.session.commit()
        return {'response': {'user deleted': int(_user)}}


# May be needed, same as Users.post() except it needs to be left unprotected - JWT Nov 2016
class Signup(Resource):
    def post(self):
        return {'response': 'I signed up!!!'}
    def get(self):
        return {'message': 'No GET method for this endpoint.'}


class Logout(Resource):
    def post(self):
        return {'response': 'I''m logged out!!!'}
    def get(self):
        return {'message': 'No GET method for this endpoint.'}

class DisableUser(Resource):
    def post(self):
        return {'response': 'Created new user!!!'}
    def get(self, id):
        return {'message': 'No GET method for this endpoint.'}

api.add_resource(TodoItem, '/todos/<int:id>')
api.add_resource(SecureMe, '/secureme/<int:id>')
api.add_resource(Logout, '/logout')
api.add_resource(Users, '/users', '/user/<string:_user>')
api.add_resource(DisableUser, '/user/<string:_user>/disable')
