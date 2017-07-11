(function () {
    'use strict';

    angular
        .module('app')
        .factory('ReposService', Service);

    function Service($http, $q, __env) {
        var factory = {
              _get_repos: get_repos
            , _create_repo: create_repo
            , _update_repo: update_repo
            , _delete_repo: delete_repo
        };

        return factory;

        function get_repos() {
            var deferred = $q.defer();
            $http.get(__env.api_url + ':' + __env.port + '/api/v2/repos')
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

        function create_repo() {
            var deferred = $q.defer();
            return deferred.promise;
        }

        function update_repo() {
            var deferred = $q.defer();
            return deferred.promise;
        }

        function delete_repo() {
            var deferred = $q.defer();
            return deferred.promise;
        }
    }
})();
