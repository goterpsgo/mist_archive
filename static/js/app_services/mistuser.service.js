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
            // , _get_stuff: get_stuff
        };

        return factory;

        // function get_stuff() {
        //     console.log('[21] Got here');
        //     return $http.get('http://10.11.1.239:8080/api/v2/stuff')
        //         .then(function(response) {
        //             console.log('[24] Got here');
        //             return response.data;
        //         })
        // }

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
            $http.get('http://10.11.1.239:8080/api/v2/users')
                .then(
                    function(response) {
                        deferred.resolve(response.data);
                    }
                );
            return deferred.promise;
        }

        function get_user(id) {
            var deferred = $q.defer();
            $http.get('http://10.11.1.239:8080/api/v2/user/' + id)
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
            var config = {
                headers : {
                    'Content-Type': 'application/json;charset=utf-8;'
                }
            }
            var deferred = $q.defer();
            form_data.repos = serial_to_obj(form_data.repos);   // converting delimited strings into JSON objects
            $http.post('http://10.11.1.239:8080/api/v2/user/signup', form_data, config)
                .success(function(form_data, status, headers, config) {
                    console.log('[68] My form_data: ' + form_data);
                })
                .error(function(data, status, headers, config) {
                    console.log('[71] It didn\'t work :( ');
                })
            ;
            return deferred.promise;
        }

        function update_user() {
            var deferred = $q.defer();
            return deferred.promise;
        }

        function delete_user() {
            var deferred = $q.defer();
            return deferred.promise;
        }
    }
})();
