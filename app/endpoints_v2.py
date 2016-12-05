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
        , 'permission_id_new': obj_user.permission_id
        , 'subject_dn': obj_user.subjectDN
        , 'first_name': obj_user.firstName
        , 'last_name': obj_user.lastName
        , 'organization': obj_user.organization
        , 'lockout': obj_user.lockout
        , 'permission_name': obj_user.permissions.name
        , 'permission': obj_user.permission
        , 'repos': {}
        , 'cnt_repos': 0    # if a user has at least one repo assigned then value > 0
    }

    # 2. Generate collection of repo dicts, selecting only repoID, scID, serverName, and repoName
    # NOTE: single distinct() may still result in multiples of identical rows in large recordsets - JWT 28 Nov 2016
    rs_repos_handle = rs_repos().with_entities(main.Repos.repoID.distinct(), main.Repos.scID, main.Repos.serverName, main.Repos.repoName)

    # 3. Generate collection of requested repos and save it to users dict
    rs_requested_repos_access_handle = rs_request_user_access()
    # Get all the SCs and repo data affiliated with a given obj_user.id
    obj_requested_repos_access = rs_requested_repos_access_handle.filter(main.requestUserAccess.userID == int(obj_user.id))

    # Get the rest of the repo data using the information collected in obj_requested_repos_access
    for obj_requested_repo_access in obj_requested_repos_access:
        obj_repos = rs_repos_handle.filter(main.and_(main.Repos.scID == obj_requested_repo_access.scID, main.Repos.repoID == obj_requested_repo_access.repoID))

        # Run if there's one or more rows returned from obj_repos
        if int(obj_repos.count()) != 0:
            # Create user['repos'] if needed
            for obj_repo in obj_repos:
                identifier = obj_repo.serverName + "," + obj_repo.repoName + "," + str(obj_requested_repo_access.repoID) + "," + str(obj_requested_repo_access.scID)
                repo_data = str(obj_user.id) + "," + str(obj_requested_repo_access.scID) + "," + str(obj_requested_repo_access.repoID) + "," + obj_user.username # used to populate UserAccess and requestUserAccess tables
                # NOTE: Bootstrap default CSS checkbox-inline used for "cursor: pointer" to indicate clickable resource
                repo = {
                      'server_name': obj_repo.serverName
                    , 'repo_name': obj_repo.repoName
                    , 'repoID': obj_requested_repo_access.repoID
                    , 'scID': obj_requested_repo_access.scID
                    , 'is_assigned': 0
                    , 'identifier': identifier
                    , 'repo_data': repo_data
                    , 'class': 'checkbox-inline text-primary'
                }
                user['repos'][identifier] = repo

    # 4. Generate collection of assigned repos and save it to users dict
    rs_repos_access_handle = rs_user_access()
    # Get all the SCs and repo data affiliated with a given obj_user.id
    obj_repos_access = rs_repos_access_handle.filter(main.UserAccess.userID == int(obj_user.id))

    # Get the rest of the repo data using the information collected in obj_repos_access
    for obj_repo_access in obj_repos_access:
        obj_repos = rs_repos_handle.filter(main.and_(main.Repos.scID == obj_repo_access.scID, main.Repos.repoID == obj_repo_access.repoID))

        # Run if there's one or more rows returned from obj_repos
        if int(obj_repos.count()) != 0:
            for obj_repo in obj_repos:
                identifier = obj_repo.serverName + "," + obj_repo.repoName + "," + str(obj_repo_access.repoID) + "," + str(obj_repo_access.scID)
                repo_data = str(obj_user.id) + "," + str(obj_repo_access.scID) + "," + str(obj_repo_access.repoID) + "," + obj_user.username # used to populate UserAccess and requestUserAccess tables
                # NOTE: Bootstrap default CSS checkbox-inline used for "cursor: pointer" to indicate clickable resource
                repo = {
                      'server_name': obj_repo.serverName
                    , 'repo_name': obj_repo.repoName
                    , 'repoID': obj_repo_access.repoID
                    , 'scID': obj_repo_access.scID
                    , 'is_assigned': 1
                    , 'identifier': identifier
                    , 'repo_data': repo_data
                    , 'class': 'checkbox-inline'
                }
                # Add repo if key doesn't yet exist in users['repos'] dict
                if ("identifier" not in user['repos']):
                    user['repos'][identifier] = repo
            user['cnt_repos'] += 1    # if a user has at least one repo assigned then value > 0
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
    # Do I even needs this method?!?! Maybe for reference. - JWT 5 Dec 2016
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
            main.session.add(new_user)
            main.session.begin_nested()

            for user_repo in form_fields['repos']:
                new_user_access = main.UserAccess(
                      repoID = user_repo['repo_id']
                    , scID = user_repo['sc_id']
                    , userID = new_user.id
                    , userName = form_fields['username']
                )
                main.session.add(new_user_access)
                main.session.begin_nested()

            main.session.commit()
            main.session.flush()

            return {'response': {'method': 'POST', 'result': 'success', 'message': 'New user added.', 'class': 'alert alert-success', 'user_id': int(new_user.id)}}

        except (main.IntegrityError) as e:
            print ("[ERROR] POST /api/v2/users / ID: %s / %s" % (request.get_json(force=True)['username'],e))
            main.session.rollback()
            return {'response': {'method': 'POST', 'result': 'error', 'message': 'Submitted username already exists.', 'class': 'alert alert-warning'}}

    @jwt_required()
    # for a given user ID:
    # 1. Update simple fields directly into mistUsers table
    # 2. Extract user ID, username, delete all userAccess rows with that user ID, and insert new rows with user ID, username, scID, and repoID
    # 3. Update permission in mistUsers table
    def put(self, _user):
        try:
            form_fields = request.get_json(force=True)
            permission = form_fields['permission']

            # Set aside any non-MistUser-specific values
            user_admin_toggle = None
            if ("user_admin_toggle" in form_fields):
                user_admin_toggle = form_fields.pop('user_admin_toggle')
            this_user = main.session.query(main.MistUser).filter(main.MistUser.id == int(_user))

            repo = None
            if ("repo" in form_fields):
                repo = {}
                repo['userID'], repo['scID'], repo['repoID'], repo['userName'] = form_fields.pop('repo').split(',')

            # currently provided by Users.get(), currently not needed - JWT 5 Dec 2016
            cnt_repos = None
            if ("cnt_repos" in form_fields):
                cnt_repos = form_fields.pop('cnt_repos')

            # ==================================================
            # UPDATE GENERAL USER DATA

            # Pass _user value to get mistUser object and update with values in form_fields
            if ("password" in form_fields):
                form_fields["password"] = hashlib.sha256(form_fields["password"]).hexdigest()
            if (any(form_fields)):
                this_user.update(form_fields)
                db_fields = {}
            main.session.begin_nested()

            # ==================================================
            # TOGGLE USER ADMIN ASSIGNMENTS
            if (user_admin_toggle is not None):

                upd_form = {}
                if (user_admin_toggle > 0):
                    upd_form = {
                        "permission": 2 if permission == 1 else 1   # regular user perms if user has at least one repos assigned
                    }
                else:
                    upd_form = {
                        "permission": 2 if permission == 0 else 0   # no perms if user has no repos assigned
                    }
                this_user.update(upd_form)
                main.session.begin_nested()

            # ==================================================
            # TOGGLE USER REPO ASSIGNMENTS

            # Extract only simple fields (ie not permission, repos) and copy them into db_fields
            if (repo is not None):
                repo['userID'] = int(repo['userID'])
                repo['scID'] = str(repo['scID'])
                repo['repoID'] = int(repo['repoID'])
                repo['userName'] = str(repo['userName'])
                # repo = {key:str(value) for key, value in repo.iteritems()}  # convert to string values

                # Flush any exceptions currently in session
                # main.session.rollback()

                # All repo assignments are saved in requestUserAccess table
                # Repo assignments are marked as approved if also saved in UserAccess table
                # obj_repos = rs_repos_handle.filter(main.and_(main.Repos.scID == obj_repo_access.scID, main.Repos.repoID == obj_repo_access.repoID))
                userAccessEntry = main.session.query(main.UserAccess)\
                    .filter(main.and_(main.UserAccess.userID == repo['userID'], main.UserAccess.scID == repo['scID'], main.UserAccess.repoID == repo['repoID']))

                requestUserAccessEntry = main.session.query(main.requestUserAccess)\
                    .filter(main.and_(main.requestUserAccess.userID == repo['userID'], main.requestUserAccess.scID == repo['scID'], main.requestUserAccess.repoID == repo['repoID']))

                # Toggle repo entry between requested and assigned
                if (userAccessEntry.first() is None):   # If user requested to use that repo, and the repo/user assignment is not in userAccessEntry...
                    new_repo = main.UserAccess(
                          userID = repo['userID']
                        , scID = repo['scID']
                        , repoID = repo['repoID']
                        , userName = repo['userName']
                    )
                    main.session.add(new_repo)  # maybe remove one day? - JWT 1 Dec 2016

                    # # Ignore permission toggle if user is admin
                    # if (this_user_permission < 2):
                    #     upd_form = {
                    #         "permission": 1 if (cnt_repos is not None and permission != 0) else 0
                    #     }
                    #     print "[397] upd_form: %r" % upd_form
                    #     this_user.update(upd_form)

                    main.session.begin_nested()
                    cnt_repos += 1
                    # userAccessEntry.is_assigned = main.current_timestamp  # currently not needed - JWT 2 Dec 2016
                else:                                # add to requested to set as requested
                    userAccessEntry.delete()  # maybe remove one day? - JWT 1 Dec 2016
                    main.session.begin_nested()
                    cnt_repos -= 1
                    # # Ignore permission toggle if user is admin
                    # if (this_user_permission < 2):
                    #     upd_form = {
                    #         "permission": 1 if (cnt_repos is not None and permission != 0) else 0
                    #     }
                    #     print "[412] upd_form: %r" % upd_form
                    #     this_user.update(upd_form)
                    # userAccessEntry.is_assigned = main.current_timestamp  # currently not needed - JWT 2 Dec 2016

                # Mark any non-admin user with one or more assigned repos as having user permissions.
                if (permission < 2):
                    upd_form = {
                        "permission": 1 if (cnt_repos > 0) else 0
                    }
                    this_user.update(upd_form)
                    main.session.begin_nested()

            main.session.commit()
            main.session.flush()

            return {'response': {'method': 'PUT', 'result': 'success', 'message': 'User successfully updated.', 'class': 'alert alert-success', 'user_id': int(_user)}}

        except (AttributeError) as e:
            print ("[AttributeError] PUT /api/v2/user/%s / %s" % (_user,e))
            main.session.rollback()
            return {'response': {'method': 'PUT', 'result': 'AttributeError', 'message': e, 'class': 'alert alert-danger'}}
        except (main.ProgrammingError) as e:
            print ("[ProgrammingError] PUT /api/v2/user/%s / %s" % (_user,e))
            main.session.rollback()
            return {'response': {'method': 'PUT', 'result': 'ProgrammingError', 'message': e, 'class': 'alert alert-danger'}}
        except (TypeError) as e:
            print ("[TypeError] PUT /api/v2/user/%s / %s" % (_user,e))
            main.session.rollback()
            return {'response': {'method': 'PUT', 'result': 'TypeError', 'message': 'TypeError', 'class': 'alert alert-danger'}}
        except (main.NoSuchColumnError) as e:
            print ("[NoSuchColumnError] PUT /api/v2/user/%s / %s" % (_user,e))
            main.session.rollback()
            return {'response': {'method': 'PUT', 'result': 'NoSuchColumnError', 'message': e, 'class': 'alert alert-danger'}}

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
        if re.match('^[0-9]+$', _user):
            # use int value for .id
            return {'response': {'method': 'DELETE', 'result': 'success', 'message': 'User successfully deleted.', 'class': 'alert alert-success', 'user_id': int(_user)}}
        else:
            # use str value for .username
            return {'response': {'method': 'DELETE', 'result': 'success', 'message': 'User successfully deleted.', 'class': 'alert alert-success', 'user_id': _user}}


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
            main.session.add(new_user)
            main.session.begin_nested()

            for user_repo in form_fields['repos']:
                new_user_access = main.requestUserAccess(
                      repoID = int(user_repo['repo_id'])
                    , scID = user_repo['sc_id']
                    , userID = new_user.id
                    , userName = form_fields['username']
                )
                main.session.begin_nested()

            main.session.commit()
            main.session.flush()

            return {'response': {'method': 'POST', 'result': 'success', 'message': 'User information submitted. Information will be reviewed and admin will contact you when approved.', 'class': 'alert alert-success', 'user_id': int(new_user.id)}}

        except (ValueError) as e:
            print ("[ERROR] POST /api/v2/user/signupuser / ID: %s / %s" % (request.get_json(force=True)['username'], e))
            main.session.rollback()
            return {'response': {'method': 'POST', 'result': 'error', 'message': str(e), 'class': 'alert alert-danger'}}
        except (main.IntegrityError) as e:
            print ("[ERROR] POST /api/v2/user/signupuser / ID: %s / %s" % (request.get_json(force=True)['username'],e))
            main.session.rollback()
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


api.add_resource(TodoItem, '/todos/<int:id>')
api.add_resource(SecureMe, '/secureme/<int:id>')
api.add_resource(Users, '/users', '/user/<string:_user>')
api.add_resource(Signup, '/user/signup')
api.add_resource(Repos, '/user/repos')
