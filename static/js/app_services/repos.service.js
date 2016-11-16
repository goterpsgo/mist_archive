(function () {
    'use strict';

    angular
        .module('app')
        .factory('ReposService', Service);

    function Service($http, $q) {
        var factory = {
              _get_repos: get_repos
            , _create_repo: create_repo
            , _update_repo: update_repo
            , _delete_repo: delete_repo
        };

        return factory;

        function get_repos() {
            var deferred = $q.defer();
            $http.get('http://10.11.1.239:8443/api/v2/user/repos')
                .then(
                    function(response) {
                        deferred.resolve(response.data);
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
