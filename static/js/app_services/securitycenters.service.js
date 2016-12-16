(function () {
    'use strict';

    angular
        .module('app')
        .factory('SecurityCentersService', Service);

    function Service($http, $q) {
        var factory = {
              _get_scs: get_scs
            , _get_sc: get_sc
            , _create_sc: create_sc
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
            $http.get('https://10.11.1.239:8444/api/v2/securitycenters')
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
            $http.get('https://10.11.1.239:8444/api/v2/securitycenter/' + id)
                .then(
                    function(response) {
                        deferred.resolve(response.data);
                    }
                );
            return deferred.promise;
        }

        function create_sc(form_data) {
            var deferred = $q.defer();
            var config = {
                headers : {
                    'Content-Type': 'application/json;charset=utf-8;'
                }
            }

            $http.post('https://10.11.1.239:8444/api/v2/securitycenters', form_data, config)
                .success(function(form_data, status, headers, config) {
                    deferred.resolve(form_data);
                })
                .error(function(data, status, headers, config) {
                    deferred.resolve(JSON.parse('{"response": {"method": "POST", "result": "error", "status": "' + status + '"}}'));
                })
            ;
            return deferred.promise;
        }

        function update_sc(id, form_data) {
            var deferred = $q.defer();
            var config = {
                headers : {
                    'Content-Type': 'application/json;charset=utf-8;'
                }
            };
            console.log('[mistuser.service:95] id: ' + id);
            console.log(form_data);


            $http.put('https://10.11.1.239:8444/api/v2/securitycenter/' + id, form_data, config)
                .success(function(form_data, status, headers, config) {
                    deferred.resolve(form_data);
                })
                .error(function(data, status, headers, config) {
                    deferred.resolve(JSON.parse('{"response": {"method": "POST", "result": "error", "status": "' + status + '"}}'));
                })
            ;
            return deferred.promise;
        }

        function delete_sc(id) {
            console.log('[mistuser.service:94] delete: ' + id);
            var deferred = $q.defer();
            var config = {
                headers : {
                    'Content-Type': 'application/json;charset=utf-8;'
                }
            };

            console.log('[mistuser.service:102] before delete');
            $http.delete('https://10.11.1.239:8444/api/v2/securitycenter/' + id)
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
