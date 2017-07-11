(function () {
    'use strict';

    angular
        .module('app')
        .factory('SubjectDNService', Service);

    function Service($http, $q, __env) {
        var factory = {
            _get_subjectdn: get_subjectdn
        };

        return factory;

        function get_subjectdn() {
            var deferred = $q.defer();
            $http.get(__env.api_url + ':' + __env.port + '/api/v2/subjectdn')
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
