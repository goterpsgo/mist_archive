(function () {
    'use strict';

    angular
        .module('app')
        .factory('TagDefinitionsService', Service);

    function Service($http, $q, __env) {
        var factory = {
              _get_tagdefinitions: get_tagdefinitions
            , _delete_tagdefinitions: delete_tagdefinitions
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

        function delete_tagdefinitions(id) {
            var deferred = $q.defer();
            var config = {
                headers : {
                    'Content-Type': 'application/json;charset=utf-8;'
                }
            };

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
