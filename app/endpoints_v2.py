from flask import Blueprint, jsonify, request, render_template, current_app, make_response
from flask_restful import Resource, Api, reqparse, abort
from flask_jwt import JWT, jwt_required, current_identity
from mist_main import return_app
import sqlalchemy
from sqlalchemy.orm import scoped_session
from common.models import main, base_model
from common.db_helpers import PasswordCheck
import re
import hashlib
import config
import json
import requests
import socket

api_endpoints = Blueprint('mist_auth', __name__, url_prefix="/api/v2")
api = Api(api_endpoints)
this_app = return_app()


def rs_users():
    return main.session.query(main.MistUser).join(main.UserPermission, main.MistUser.permission_id == main.UserPermission.id)

def rs_user_access():
    return main.session.query(main.UserAccess)

def rs_request_user_access():
    return main.session.query(main.requestUserAccess)

def rs_repos():
    return main.session.query(main.Repos)


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
        try:
            main.session.rollback()
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
        except (main.ResourceClosedError) as e:
            return {'response': {'method': 'GET', 'result': 'error', 'message': e, 'class': 'alert alert-warning'}}
        except (IOError) as e:
            return {'response': {'method': 'GET', 'result': 'error', 'message': e, 'class': 'alert alert-warning'}}
        except (AttributeError) as e:
            return {'response': {'method': 'GET', 'result': 'error', 'message': e, 'class': 'alert alert-warning'}}
        except (main.StatementError) as e:
            return {'response': {'method': 'GET', 'result': 'error', 'message': e, 'class': 'alert alert-warning'}}


def authenticate(username, password):
    main.session.rollback()
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
    # 1. Generate user dict
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

    # 2. Generate collection of repo dicts, selecting only repoID, scID, serverName, and repoName
    # NOTE: single distinct() may still result in multiples of identical rows in large recordsets - JWT 28 Nov 2016
    rs_repos_handle = rs_repos().with_entities(main.Repos.repoID.distinct(), main.Repos.scID, main.Repos.serverName, main.Repos.repoName)

    # 3. Generate collection of assigned repos and save it to users dict
    assigned = []
    rs_repos_access_handle = rs_user_access()
    # Get all the SCs and repo data affiliated with a given obj_user.id
    obj_repos_access = rs_repos_access_handle.filter(main.UserAccess.userID == int(obj_user.id))

    # Get the rest of the repo data using the information collected in obj_repos_access
    for obj_repo_access in obj_repos_access:
        obj_repos = rs_repos_handle.filter(main.and_(main.Repos.scID == obj_repo_access.scID, main.Repos.repoID == obj_repo_access.repoID))

        # Run if there's one or more rows returned from obj_repos
        if int(obj_repos.count()) != 0:
            # Create user['repos'] if needed
            if (user.has_key('repos') == False):
                user['repos'] = {}
            for obj_repo in obj_repos:
                repo = {
                      'server_name': obj_repo.serverName
                    , 'repo_name': obj_repo.repoName
                    , 'repoID': obj_repo_access.repoID
                    , 'scID': obj_repo_access.scID
                }
                assigned.append(repo)
            user['repos']['assigned'] = assigned
    assigned = None

    # 4. Generate collection of requested repos and save it to users dict
    requested = []
    rs_requested_repos_access_handle = rs_request_user_access()
    # Get all the SCs and repo data affiliated with a given obj_user.id
    obj_requested_repos_access = rs_requested_repos_access_handle.filter(main.requestUserAccess.userID == int(obj_user.id))

    # Get the rest of the repo data using the information collected in obj_requested_repos_access
    for obj_requested_repo_access in obj_requested_repos_access:
        obj_repos = rs_repos_handle.filter(main.and_(main.Repos.scID == obj_requested_repo_access.scID, main.Repos.repoID == obj_requested_repo_access.repoID))

        # Run if there's one or more rows returned from obj_repos
        if int(obj_repos.count()) != 0:
            # Create user['repos'] if needed
            if (user.has_key('repos') == False):
                user['repos'] = {}
            for obj_repo in obj_repos:
                repo = {
                      'server_name': obj_repo.serverName
                    , 'repo_name': obj_repo.repoName
                    , 'repoID': obj_repo_access.repoID
                    , 'scID': obj_repo_access.scID
                }
                requested.append(repo)
            user['repos']['requested'] = requested
    requested = None

    return user

def create_repo_dict(obj_repo):
    repo = {
          'repo_id': obj_repo.repoID
        , 'sc_id': obj_repo.scID
        , 'repo_name': obj_repo.repoName
        , 'server_name': obj_repo.serverName
    }
    return repo


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
            main.session.rollback()
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

        except (main.NoResultFound) as e:
            return {'response': {'method': 'GET', 'result': 'error', 'message': e, 'class': 'alert alert-warning'}}
        except (main.ProgrammingError) as e:
            return {'response': {'method': 'GET', 'result': 'error', 'message': e, 'class': 'alert alert-warning'}}
        except (main.StatementError) as e:
            main.session.rollback()
            return {'response': {'method': 'GET', 'result': 'error', 'message': e, 'class': 'alert alert-warning'}}
        except (main.OperationalError) as e:
            return {'response': {'method': 'GET', 'result': 'error', 'message': e, 'class': 'alert alert-warning'}}
        except (main.InvalidRequestError) as e:
            main.session.rollback()
            return {'response': {'method': 'GET', 'result': 'error', 'message': e, 'class': 'alert alert-warning'}}
        except (main.ResourceClosedError) as e:
            return {'response': {'method': 'GET', 'result': 'error', 'message': e, 'class': 'alert alert-warning'}}

    @jwt_required()
    # 1. Inserts new user into mistUsers table and returns user id
    # 2. Inserts repo and user association into userAccess table
    def post(self):
        try:
            form_fields = request.get_json(force=True)

            new_user = main.MistUser(
                  username=form_fields['username']
                , password=hashlib.sha256(form_fields['password0']).hexdigest()
                , subjectDN=form_fields['subject_dn']
                , firstName=form_fields['first_name']
                , lastName=form_fields['last_name']
                , organization=form_fields['organization']
                , lockout="No"
                , permission_id=2
            )
            main.session.rollback()
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

            return {'response': {'method': 'POST', 'result': 'success', 'message': 'New user added.', 'class': 'alert alert-success', 'user_id': int(new_user.id)}}

        except (main.IntegrityError) as e:
            print ("[ERROR] POST /api/v2/users / ID: %s / %s" % (request.get_json(force=True)['username'],e))
            return {'response': {'method': 'POST', 'result': 'error', 'message': 'Submitted username already exists.', 'class': 'alert alert-warning'}}

    @jwt_required()
    # for a given user ID:
    # 1. Update simple fields directly into mistUsers table
    # 2. Extract user ID, username, delete all userAccess rows with that user ID, and insert new rows with user ID, username, scID, and repoID
    # 3. Update permission in mistUsers table
    def put(self, _user):
        try:
            form_fields = request.get_json(force=True)

            # Extract only simple fields (ie not permission, repos) and copy them into db_fields
            db_fields = {}
            for key, value in form_fields.iteritems():
                if (key != "repos"):
                    db_fields[key] = value
                if (key == "password"):
                    db_fields[key] = hashlib.sha256(value).hexdigest()

            # Flush any exceptions currently in session
            main.session.rollback()

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

            return {'response': {'method': 'PUT', 'result': 'success', 'message': 'User successfully updated.', 'class': 'alert alert-success', 'user_id': int(_user)}}

        except (AttributeError) as e:
            print ("[ERROR] PUT /api/v2/user/signupuser/%s / %s" % (_user,e))
            return {'response': {'method': 'PUT', 'result': 'error', 'message': 'User doesn\'t exist.', 'class': 'alert alert-danger'}}

    @jwt_required()
    # removes user and their affiliated repos
    def delete(self, _user):
        if re.match('^[0-9]+$', _user):
            # use int value for .id
            main.session.query(main.requestUserAccess).filter(main.requestUserAccess.userID == int(_user)).delete()
            main.session.query(main.UserAccess).filter(main.UserAccess.userID == int(_user)).delete()
            main.session.query(main.MistUser).filter(main.MistUser.id == int(_user)).delete()
        else:
            # use str value for .username
            main.session.query(main.requestUserAccess).filter(main.requestUserAccess.userName == _user).delete()
            main.session.query(main.UserAccess).filter(main.UserAccess.userName == _user).delete()
            main.session.query(main.MistUser).filter(main.MistUser.username == _user).delete()

        main.session.commit()
        return {'response': {'method': 'DELETE', 'result': 'success', 'message': 'User successfully deleted.', 'class': 'alert alert-success', 'user_id': int(_user)}}


class Signup(Resource):
    def get(self):
        return {'message': 'No GET method for this endpoint.'}
    def post(self):
        try:
            form_fields = request.get_json(force=True)

            # If passwords do not match...
            if (form_fields['password0'] != form_fields['password1']):
                raise ValueError("Password error: passwords do not match.")

            # If password does not fulfill complexity criteria...
            pw_complexity = PasswordCheck(form_fields['password0'])
            error = pw_complexity.check_password()
            if error:
                raise ValueError("Password error: " + error)

            new_user = main.MistUser(
                  username=form_fields['username']
                , password=hashlib.sha256(form_fields['password0']).hexdigest()
                , subjectDN="No certs"
                , firstName=form_fields['first_name']
                , lastName=form_fields['last_name']
                , organization=form_fields['organization']
                , lockout="No"
                , permission=0
                , permission_id=1
            )
            main.session.rollback()
            main.session.add(new_user)
            main.session.commit()
            main.session.flush()

            for user_repo in form_fields['repos']:
                new_user_access = main.requestUserAccess(
                      repoID = int(user_repo['repo_id'])
                    , scID = user_repo['sc_id']
                    , userID = new_user.id
                    , userName = form_fields['username']
                )
                main.session.add(new_user_access)
                main.session.commit()
                main.session.flush()

            return {'response': {'method': 'POST', 'result': 'success', 'message': 'User information submitted. Information will be reviewed and admin will contact you when approved.', 'class': 'alert alert-success', 'user_id': int(new_user.id)}}

        except (ValueError) as e:
            print ("[ERROR] POST /api/v2/user/signupuser / ID: %s / %s" % (request.get_json(force=True)['username'], e))
            return {'response': {'method': 'POST', 'result': 'error', 'message': str(e), 'class': 'alert alert-danger'}}

        except (main.IntegrityError) as e:
            print ("[ERROR] POST /api/v2/user/signupuser / ID: %s / %s" % (request.get_json(force=True)['username'],e))
            return {'response': {'method': 'POST', 'result': 'error', 'message': 'Submitted username already exists.', 'class': 'alert alert-danger'}}

    def put(self, _user=None):
        return {'message': 'No PUT method for this endpoint.'}
    def delete(self, _user=None):
        return {'message': 'No DELETE method for this endpoint.'}


class Repos(Resource):
    # @jwt_required()
    def get(self):
        # returns list of repos from Repos table
        # (NOTE: since there's no dedicated normalized table for just repos, all combinations of returned fields from Repos are distinct)
        rs_dict = dict()    # used to hold and eventually return repos_list[] recordset and associated metadata
        # rs_dict['Authorization'] = create_new_token(request)   # pass token via response data since I can't figure out how to pass it via response header - JWT Oct 2016

        # NOTE: main.Repos.id is not being returned since Repos table is not properly normalized and including id will result in returning duplicates - JWT 7 Nov 2016
        main.session.rollback()
        rs_repos_handle = rs_repos().group_by(main.Repos.repoID, main.Repos.scID, main.Repos.repoName, main.Repos.serverName)\
            .order_by(main.Repos.serverName, main.Repos.repoName)

        # add results to users_list[]
        repos_list = []
        for r_repo in rs_repos_handle:
            repos_list.append(create_repo_dict(r_repo))
        rs_dict['repos_list'] = repos_list  # add users_list[] to rs_dict

        return jsonify(rs_dict) # return rs_dict
    def post(self):
        # TODO: will use for inserting new repo entries
        form_fields = request.get_json(force=True)
        return {'response': {'foo': form_fields}}
    def put(self, _user=None):
        # TODO: will use for updating existing repo entries
        return {'message': 'No PUT method for this endpoint.'}
    def delete(self, _user=None):
        # TODO: will use for deleting repo entries
        return {'message': 'No DELETE method for this endpoint.'}


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
api.add_resource(Signup, '/user/signup')
api.add_resource(Repos, '/user/repos')
api.add_resource(DisableUser, '/user/<string:_user>/disable')
