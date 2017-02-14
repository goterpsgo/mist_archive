(function () {
    'use strict';

    angular
        .module('app')
        .factory('AssetsService', Service);

    function Service($http, $q, __env) {
        var factory = {
              _get_assets: get_assets
        };

        return factory;

        function get_assets() {
            var deferred = $q.defer();
            $http.get(__env.api_url + ':' + __env.port + '/api/v2/assets')
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

        function insert_taggedrepos(form_data) {
            var deferred = $q.defer();
            var config = {
                headers : {
                    'Content-Type': 'application/json;charset=utf-8;'
                }
            }

            $http.post(__env.api_url + ':' + __env.port + '/api/v2/taggedrepos', form_data, config)
                .then(function(form_data, status, headers, config) {
                    deferred.resolve(form_data);
                }
                , function(data, status, headers, config) {
                    // deferred.resolve(response.data.response);
                    deferred.resolve(JSON.parse('{"response": {"method": "POST", "result": "error", "status": "' + status + '"}}'));
                });
            return deferred.promise;
        }

        function delete_taggedrepos(_tagged_repo_id) {
            var deferred = $q.defer();

            $http.delete(__env.api_url + ':' + __env.port + '/api/v2/taggedrepos/' + _tagged_repo_id)
                .then(function(result) {
                    deferred.resolve(result);
                }
                , function(data, status, headers, config) {
                    // deferred.resolve(response.data.response);
                    deferred.resolve(JSON.parse('{"response": {"method": "DELETE", "result": "error", "status": "' + status + '"}}'));
                });
            return deferred.promise;
        }
    }
})();
