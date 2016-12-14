(function () {
    'use strict';

    angular
        .module('app')
        .factory('MistUsersService', Service);

    function Service($http, $q) {
        var factory = {
              _get_users: get_users
            , _get_user: get_user
            , _create_user: create_user
            , _update_user: update_user
            , _delete_user: delete_user
            , _signup_user: signup_user
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
            $http.get('https://10.11.1.239:8444/api/v2/users')
                .then(
                    function(response) {
                        deferred.resolve(response.data);
                    }
                );
            return deferred.promise;
        }

        function get_user(id) {
            var deferred = $q.defer();
            $http.get('https://10.11.1.239:8444/api/v2/user/' + id)
                .then(
                    function(response) {
                        deferred.resolve(response.data);
                    }
                );
            return deferred.promise;
        }

        function create_user() {
            var deferred = $q.defer();
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

            $http.post('https://10.11.1.239:8444/api/v2/user/signup', form_data, config)
                .success(function(form_data, status, headers, config) {
                    deferred.resolve(form_data);
                })
                .error(function(data, status, headers, config) {
                    deferred.resolve(JSON.parse('{"response": {"method": "POST", "result": "error", "status": "' + status + '"}}'));
                })
            ;
            return deferred.promise;
        }

        function update_user(id, form_data) {
            var deferred = $q.defer();
            var config = {
                headers : {
                    'Content-Type': 'application/json;charset=utf-8;'
                }
            };
            console.log('[mistuser.service:95] id: ' + id);
            console.log(form_data);


            $http.put('https://10.11.1.239:8444/api/v2/user/' + id, form_data, config)
                .success(function(form_data, status, headers, config) {
                    deferred.resolve(form_data);
                })
                .error(function(data, status, headers, config) {
                    deferred.resolve(JSON.parse('{"response": {"method": "POST", "result": "error", "status": "' + status + '"}}'));
                })
            ;
            return deferred.promise;
        }

        function delete_user(id) {
            console.log('[mistuser.service:94] delete: ' + id);
            var deferred = $q.defer();
            var config = {
                headers : {
                    'Content-Type': 'application/json;charset=utf-8;'
                }
            };

            console.log('[mistuser.service:102] before delete');
            $http.delete('https://10.11.1.239:8444/api/v2/user/' + id)
                .success(function(data, status, headers) {
                    console.log('[mistuser.service:105] delete success');
                    deferred.resolve(data);
                })
                .error(function(data, status, header, config) {
                    console.log('[mistuser.service:109] delete error');
                    deferred.resolve(JSON.parse('{"response": {"method": "POST", "result": "error", "status": "' + status + '"}}'));
                })
            ;
            return deferred.promise;
        }
    }
})();
