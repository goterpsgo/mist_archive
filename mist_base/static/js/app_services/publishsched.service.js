(function () {
    'use strict';

    angular
        .module('app')
        .factory('PublishSchedService', Service);

    function Service($http, $q, __env) {
        var factory = {
              _get_publishsched: get_publishsched
            , _delete_publishsched: delete_publishsched
            , _update_publishsched: update_publishsched
            , _insert_publishsched: insert_publishsched
        };

        return factory;

        function get_publishsched() {
            var deferred = $q.defer();
            $http.get(__env.api_url + ':' + __env.port + '/api/v2/publishsched')
                .then(
                    function(response) {
                        deferred.resolve(response.data);
                    }
                    , function(data, status, headers, config) {
                        // deferred.resolve(response.data.response);
                        deferred.resolve(JSON.parse('{"response": {"method": "GET", "result": "error", "status": "' + status + '"}}'));
                    }
                );
            return deferred.promise;
        }

        function insert_publishsched(form_data) {
            var deferred = $q.defer();
            var config = {
                headers : {
                    'Content-Type': 'application/json;charset=utf-8;'
                }
            }

            $http.post(__env.api_url + ':' + __env.port + '/api/v2/publishsched', form_data, config)
                .then(function(form_data, status, headers, config) {
                    deferred.resolve(form_data);
                }
                , function(data, status, headers, config) {
                    // deferred.resolve(response.data.response);
                    deferred.resolve(JSON.parse('{"response": {"method": "POST", "result": "error", "status": "' + status + '"}}'));
                });
            return deferred.promise;
        }

        function update_publishsched(id, form_data) {
            var deferred = $q.defer();
            var config = {
                headers : {
                    'Content-Type': 'application/json;charset=utf-8;'
                }
            };
            $http.put(__env.api_url + ':' + __env.port + '/api/v2/publishsched/' + id, form_data, config)
                .then(
                      function(form_data, status, headers, config) {
                        deferred.resolve(form_data);
                    }
                    , function(data, status, headers, config) {
                        // deferred.resolve(response.data.response);
                        deferred.resolve(JSON.parse('{"response": {"method": "PUT", "result": "error", "status": "' + status + '"}}'));
                    }
                );
            return deferred.promise;
        }

        function delete_publishsched(id) {
            var deferred = $q.defer();

            $http.delete(__env.api_url + ':' + __env.port + '/api/v2/publishsched/' + id)
                .then(function(data, status, headers) {
                    deferred.resolve(data);
                }
                , function(data, status, header, config) {
                    deferred.resolve(JSON.parse('{"response": {"method": "DELETE", "result": "error", "status": "' + status + '"}}'));
                }
            );
            return deferred.promise;
        }
    }
})();
