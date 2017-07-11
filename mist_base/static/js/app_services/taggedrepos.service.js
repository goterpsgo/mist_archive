(function () {
    'use strict';

    angular
        .module('app')
        .factory('TaggedReposService', Service);

    function Service($http, $q, __env) {
        var factory = {
              _insert_taggedrepos: insert_taggedrepos
            , _delete_taggedrepos: delete_taggedrepos
        };

        return factory;

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
