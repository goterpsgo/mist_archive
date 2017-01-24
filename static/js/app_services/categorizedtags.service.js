(function () {
    'use strict';

    angular
        .module('app')
        .factory('CategorizedTagsService', Service);

    function Service($http, $q, __env) {
        var factory = {
              _get_categorizedtags: get_categorizedtags
        };

        return factory;

        function get_categorizedtags(_id) {
            var deferred = $q.defer();
            $http.get(__env.api_url + ':' + __env.port + '/api/v2/categorizedtags/' + _id)
                .then(
                    function(response) {
                        deferred.resolve(response.data.tags);
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
