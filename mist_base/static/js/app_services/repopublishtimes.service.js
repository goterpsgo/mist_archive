(function () {
    'use strict';

    angular
        .module('app')
        .factory('RepoPublishTimesService', Service);

    function Service($http, $q, __env) {
        var factory = {
              _get_repopublishtimes: get_repopublishtimes
            , _get_publish_times_by_repo: get_publish_times_by_repo
        };

        return factory;

        function get_repopublishtimes() {
            var deferred = $q.defer();
            $http.get(__env.api_url + ':' + __env.port + '/api/v2/repopublishtimes')
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

        function get_publish_times_by_repo() {
            var deferred = $q.defer();
            $http.get(__env.api_url + ':' + __env.port + '/api/v2/repopublishtimes/1')
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
    }
})();
