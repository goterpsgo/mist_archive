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
            , _get_stuff: get_stuff
        };

        return factory;

        function get_stuff() {
            console.log('[21] Got here');
            return $http.get('http://10.11.1.239:8080/api/v2/stuff')
                .then(function(response) {
                    console.log('[24] Got here');
                    return response.data;
                })
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

        function get_user() {
            var deferred = $q.defer();
            return deferred.promise;
        }

        function create_user() {
            var deferred = $q.defer();
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
