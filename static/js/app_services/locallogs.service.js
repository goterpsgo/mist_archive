(function () {
    'use strict';

    angular
        .module('app')
        .factory('LocalLogsService', Service);

    function Service($http, $q, __env) {
        var factory = {
              _get_local_log: get_local_log
            , _get_local_logs: get_local_logs
        };

        return factory;

        function get_local_logs() {
            var deferred = $q.defer();
            $http.get(__env.api_url + ':' + __env.port + '/api/v2/locallogs')
                .then(
                    function(response) {
                        deferred.resolve(response.data);
                    }
                    , function(data, status, headers, config) {
                        deferred.resolve(JSON.parse('{"response": {"method": "GET", "result": "error", "status": "' + status + '"}}'));
                    }
                );
            return deferred.promise;
        }

        function get_local_log(_name) {
            var deferred = $q.defer();
            $http.get(__env.api_url + ':' + __env.port + '/api/v2/locallog/' + _name)
                .then(
                    function(response) {
                        deferred.resolve(response.data);
                    }
                    , function(data, status, headers, config) {
                        deferred.resolve(JSON.parse('{"response": {"method": "GET", "result": "error", "status": "' + status + '"}}'));
                    }
                );
            return deferred.promise;
        }
    }
})();
