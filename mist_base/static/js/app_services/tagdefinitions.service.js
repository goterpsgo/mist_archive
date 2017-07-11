(function () {
    'use strict';

    angular
        .module('app')
        .factory('TagDefinitionsService', Service);

    function Service($http, $q, __env) {
        var factory = {
              _get_tagdefinitions: get_tagdefinitions
            , _delete_tagdefinition: delete_tagdefinition
            , _update_td_param: update_td_param
            , _insert_tagdefinition: insert_tagdefinition
        };

        return factory;

        function get_tagdefinitions() {
            var deferred = $q.defer();
            $http.get(__env.api_url + ':' + __env.port + '/api/v2/tagdefinitions')
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

        function insert_tagdefinition(form_data) {
            var deferred = $q.defer();
            var config = {
                headers : {
                    'Content-Type': 'application/json;charset=utf-8;'
                }
            }

            $http.post(__env.api_url + ':' + __env.port + '/api/v2/tagdefinitions', form_data, config)
                .then(function(form_data, status, headers, config) {
                    deferred.resolve(form_data);
                }
                , function(data, status, headers, config) {
                    // deferred.resolve(response.data.response);
                    deferred.resolve(JSON.parse('{"response": {"method": "POST", "result": "error", "status": "' + status + '"}}'));
                });
            return deferred.promise;
        }

        function update_td_param(id, form_data) {
            var deferred = $q.defer();
            var config = {
                headers : {
                    'Content-Type': 'application/json;charset=utf-8;'
                }
            };
            $http.put(__env.api_url + ':' + __env.port + '/api/v2/tagdefinition/' + id, form_data, config)
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

        function delete_tagdefinition(id) {
            var deferred = $q.defer();

            $http.delete(__env.api_url + ':' + __env.port + '/api/v2/tagdefinition/' + id)
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
