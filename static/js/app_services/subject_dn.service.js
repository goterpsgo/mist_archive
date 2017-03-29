(function () {
    'use strict';

    angular
        .module('app')
        .factory('MistUsersService', Service);

    function Service($http, $q, __env) {
        var factory = {
              _get_users: get_users
            , _get_user: get_user
            , _update_user: update_user
            , _delete_user: delete_user
            , _signup_user: signup_user
        };

        var _status = ['Disabled', 'User', 'Admin'];
        var _status_class = ['btn btn-danger', 'btn btn-info', 'btn btn-primary'];
        var _lockout_modes = {
              "No": {
                  "class": "btn-info glyphicon-ok"
                , "switch_to": "Yes"
                , "desc": "Unlocked"
              }
            , "Yes": {
                  "class": "btn-danger glyphicon-lock"
                , "switch_to": "No"
                , "desc": "Locked"
              }
        };

        return factory;

        function serial_to_obj(rows, delim) {
            if (delim === undefined) {
                delim = ':';
            }

            var obj_rows = []
            for (var _cnt_rows in rows) {
                var obj_row = {};
                var row = rows[_cnt_rows];
                var fields = row.split(',');
                for (var _cnt_fields in fields) {
                    var _arr_field = fields[_cnt_fields].split(':'), key = _arr_field[0], value = _arr_field[1];
                    obj_row[key] = value;
                }
                obj_rows.push(obj_row);
            }
            return obj_rows;
        }

        function get_users() {
            var deferred = $q.defer();
            $http.get(__env.api_url + ':' + __env.port + '/api/v2/users')
                .then(
                    function(response) {
                        for (var _cnt in response.data.users_list) {
                            response.data.users_list[_cnt]['status'] = _status[response.data.users_list[_cnt].permission];
                            response.data.users_list[_cnt]['status_class'] = _status_class[response.data.users_list[_cnt].permission];
                            response.data.users_list[_cnt]['lockout_class'] = _lockout_modes[response.data.users_list[_cnt].lockout].class;
                            response.data.users_list[_cnt]['lockout_desc'] = _lockout_modes[response.data.users_list[_cnt].lockout].desc;
                            response.data.users_list[_cnt]['lockout_switch_to'] = _lockout_modes[response.data.users_list[_cnt].lockout].switch_to;
                            // if (response.data.users_list[_cnt].lockout == 'Yes') {
                            //     response.data.users_list[_cnt]['status'] = _status[0];
                            //     response.data.users_list[_cnt]['status_class'] = _status_class[0];
                            // }
                        }
                        deferred.resolve(response.data);
                    }
                    , function(data, status, headers, config) {
                        // deferred.resolve(response.data.response);
                        deferred.resolve(JSON.parse('{"response": {"method": "GET", "result": "error", "status": "' + status + '"}}'));
                    }
                );
            return deferred.promise;
        }

        function get_user(id) {
            var deferred = $q.defer();
            $http.get(__env.api_url + ':' + __env.port + '/api/v2/user/' + id)
                .then(
                    function(response) {
                        response.data.users_list[0]['status'] = _status[response.data.users_list[0].permission];
                        response.data.users_list[0]['status_class'] = _status_class[response.data.users_list[0].permission];
                        deferred.resolve(response.data);
                    }
                    , function(data, status, headers, config) {
                        // deferred.resolve(response.data.response);
                        deferred.resolve(JSON.parse('{"response": {"method": "GET", "result": "error", "status": "' + status + '"}}'));
                    }
                );
            return deferred.promise;
        }

        function signup_user(form_data) {
            var deferred = $q.defer();
            var config = {
                headers : {
                    'Content-Type': 'application/json;charset=utf-8;'
                }
            }

            // since values from pulldown is in comma delimited list, list is converted in to obj
            form_data.repos = serial_to_obj(form_data.repos);   // converting delimited strings into JSON objects

            $http.post(__env.api_url + ':' + __env.port + '/api/v2/user/signup', form_data, config)
                .then(function(form_data, status, headers, config) {
                    deferred.resolve(form_data);
                }
                , function(data, status, headers, config) {
                    // deferred.resolve(response.data.response);
                    deferred.resolve(JSON.parse('{"response": {"method": "POST", "result": "error", "status": "' + status + '"}}'));
                });
            return deferred.promise;
        }

        function update_user(id, form_data) {
            var deferred = $q.defer();
            var config = {
                headers : {
                    'Content-Type': 'application/json;charset=utf-8;'
                }
            };

            $http.put(__env.api_url + ':' + __env.port + '/api/v2/user/' + id, form_data, config)
                .then(function(form_data, status, headers, config) {
                    deferred.resolve(form_data);
                }
                , function(data, status, headers, config) {
                    deferred.resolve(JSON.parse('{"response": {"method": "PUT", "result": "error", "status": "' + status + '"}}'));
                })
            ;
            return deferred.promise;
        }

        function delete_user(id) {
            var deferred = $q.defer();

            $http.delete(__env.api_url + ':' + __env.port + '/api/v2/user/' + id)
                .then(function(data, status, headers) {
                    deferred.resolve(data);
                }
                , function(data, status, header, config) {
                    deferred.resolve(JSON.parse('{"response": {"method": "DELETE", "result": "error", "status": "' + status + '"}}'));
                })
            ;
            return deferred.promise;
        }
    }
})();
