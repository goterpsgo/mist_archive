(function () {
    'use strict';

    angular
        .module('app')
        .factory('SecurityCentersService', Service);

    function Service($http, $q, Upload) {
        var factory = {
              _get_scs: get_scs
            , _get_sc: get_sc
            , _insert_sc: insert_sc
            , _update_sc: update_sc
            , _delete_sc: delete_sc
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

        function get_scs() {
            var deferred = $q.defer();
            $http.get(__env.api_url + ':' + __env.port + '/api/v2/securitycenters')
                .then(
                    function(response) {
                        // Replace "None" with empty string
                        for (var _cnt = 0; _cnt < response.data.sc_list.length; _cnt++) {
                            Object.keys(response.data.sc_list[_cnt]).forEach(function (key) {
                                if (response.data.sc_list[_cnt][key] == 'None') {
                                    response.data.sc_list[_cnt][key] = '';
                                }
                            });
                            response.data.sc_list[_cnt]['pw'] = '';
                        }

                        deferred.resolve(response.data);
                    }
                );
            return deferred.promise;
        }

        function get_sc(id) {
            var deferred = $q.defer();
            $http.get(__env.api_url + ':' + __env.port + '/api/v2/securitycenter/' + id)
                .then(
                    function(response) {
                        deferred.resolve(response.data);
                    }
                );
            return deferred.promise;
        }

        function insert_sc(form_data) {
            var deferred = $q.defer();

            // using 3rd party module
            // https://github.com/danialfarid/ng-file-upload
            Upload.upload({
                url: __env.api_url + ':' + __env.port + '/api/v2/securitycenters'
                , data: form_data
                , method: 'POST'
            })
            .then(
                  function(response) {
                    deferred.resolve(response.data.response);
                }
                , function(response) {
                    deferred.resolve(response.data.response);
                }
            );
            return deferred.promise;
        }

        function update_sc(id, form_data) {
            var deferred = $q.defer();

            // using 3rd party module
            // https://github.com/danialfarid/ng-file-upload
            Upload.upload({
                url: __env.api_url + ':' + __env.port + '/api/v2/securitycenter/' + id
                , data: form_data
                , method: 'PUT'
            })
            .then(
                  function(response) {
                    deferred.resolve(response.data.response);
                }
                , function(response) {
                    deferred.resolve(response.data.response);
                }
            );
            return deferred.promise;
        }

        function delete_sc(id) {
            var deferred = $q.defer();
            var config = {
                headers : {
                    'Content-Type': 'application/json;charset=utf-8;'
                }
            };

            $http.delete(__env.api_url + ':' + __env.port + '/api/v2/securitycenter/' + id)
                .then(function(data, status, headers) {
                    deferred.resolve(data);
                }
                , function(data, status, header, config) {
                    deferred.resolve(JSON.parse('{"response": {"method": "POST", "result": "error", "status": "' + status + '"}}'));
                }
            );
            return deferred.promise;
        }
    }
})();
