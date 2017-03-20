from flask import Blueprint, jsonify, request, render_template, current_app, make_response
from flask_restful import Resource, Api, reqparse, abort
from flask_jwt import JWT, jwt_required, current_identity
import sys
sys.path.insert(0, "/opt/mist_base/app")
from mist_main import return_app
from common.models import main, base_model

this_app = return_app()

class BannerText(Resource):
    @jwt_required()
    def get(self, _id=None):
        try:
            rs_dict = {}  # used to hold and eventually return users_list[] recordset and associated metadata
            rs_dict['Authorization'] = create_new_token(request)  # pass token via response data since I can't figure out how to pass it via response header - JWT Oct 2016

            rs_sc_handle = rs_security_centers().order_by(main.SecurityCenter.serverName)
            r_single_sc = None
            if _id is not None:
                r_single_sc = rs_sc_handle.filter(
                    main.SecurityCenter.id == int(_id)
                ).first()

            # add results to sc_list
            sc_list = []
            if _id is None:
                for r_sc in rs_sc_handle:
                    sc_list.append(row_to_dict(r_sc))
            else:
                sc_list.append(row_to_dict(r_single_sc))

            rs_dict['sc_list'] = sc_list  # add users_list[] to rs_dict

            return jsonify(rs_dict) # return rs_dict

        except (main.NoResultFound) as e:
            print ("[NoResultFound] GET /api/v2/securitycenter %s" % e)
            return {'response': {'method': 'GET', 'result': 'error', 'message': e, 'class': 'alert alert-warning'}}
        except (AttributeError) as e:
            print ("[AttributeError] GET /api/v2/securitycenter %s" % e)
            return {'response': {'method': 'GET', 'result': 'error', 'message': e, 'class': 'alert alert-warning'}}
        except (TypeError) as e:
            print ("[TypeError] GET /api/v2/securitycenter %s" % e)
            return {'response': {'method': 'GET', 'result': 'error', 'message': e, 'class': 'alert alert-warning'}}

    @jwt_required()
    def post(self):
        try:
            form_fields = {}
            for key, value in request.form.iteritems():
                if (key != 'id' and key != 'status' and key != 'status_class'):   # don't need "id" since value is being provided by _id, may want to replace with regex in future
                    form_fields[key] = value

            if ('certificateFile' in request.files):
                certificateFile = request.files['certificateFile']
                certificateFile_name = secure_filename(certificateFile.filename)
                certificateFile.save(os.path.join(this_app.config['UPLOAD_FOLDER'] + "/" + form_fields['version'], certificateFile_name))
                form_fields['certificateFile'] = this_app.config['UPLOAD_FOLDER'] + "/" + form_fields['version'] + "/" + certificateFile_name

            if ('keyFile' in request.files):
                keyFile = request.files['keyFile']
                keyFile_name = secure_filename(keyFile.filename)
                keyFile.save(os.path.join(this_app.config['UPLOAD_FOLDER'] + "/" + form_fields['version'], keyFile_name))
                form_fields['keyFile'] = this_app.config['UPLOAD_FOLDER'] + "/" + form_fields['version'] + "/" + keyFile_name

            new_sc = main.SecurityCenter(
                  fqdn_IP = form_fields['fqdn_IP']
                , serverName = form_fields['serverName']
                , version = form_fields['version']
                , username = form_fields['username'] if ("username" in form_fields) else None
                , pw = form_fields['pw'] if ("pw" in form_fields) else None
                , certificateFile = form_fields['certificateFile'] if ("certificateFile" in form_fields) else None
                , keyFile = form_fields['keyFile'] if ("keyFile" in form_fields) else None
            )

            main.session.add(new_sc)
            main.session.commit()
            main.session.flush()

            return {'response': {'method': 'POST', 'result': 'success', 'message': 'New SecurityCenter entry submitted.', 'class': 'alert alert-success', 'user_id': int(new_sc.id)}}

        except (TypeError) as e:
            print ("[TypeError] POST /api/v2/securitycenters / %s" % e)
            main.session.rollback()
            return {'response': {'method': 'POST', 'result': 'error', 'message': str(e), 'class': 'alert alert-danger'}}
        except (ValueError) as e:
            print ("[ValueError] POST /api/v2/securitycenters / %s" % e)
            main.session.rollback()
            return {'response': {'method': 'POST', 'result': 'error', 'message': str(e), 'class': 'alert alert-danger'}}
        except (main.IntegrityError) as e:
            print ("[IntegrityError] POST /api/v2/securitycenters / %s" % e)
            main.session.rollback()
            return {'response': {'method': 'POST', 'result': 'error', 'message': 'Submitted username already exists.', 'class': 'alert alert-danger'}}

    @jwt_required()
    def delete(self, _id):
        main.session.query(main.SecurityCenter).filter(main.SecurityCenter.id == _id).delete()
        main.session.commit()
        main.session.flush()
        return {'response': {'method': 'DELETE', 'result': 'success', 'message': 'SecurityCenter successfully deleted.', 'class': 'alert alert-success', 'id': _id}}

api.add_resource(Repos, '/repos')
