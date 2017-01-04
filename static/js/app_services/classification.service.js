(function () {
    'use strict';

    angular
        .module('app')
        .factory('ClassificationService', Service);

    function Service($http, $q, __env) {
        var factory = {
              _load_classifications: load_classifications
            , _load_classification: load_classification
            , _update_classification: update_classification
        };

        return factory;

        // returns list of classifications
        function load_classifications() {
            var deferred = $q.defer();
            $http.get(__env.api_url + ':' + __env.port + '/api/v2/classifications')
                .then(
                    function(response) {
                        deferred.resolve(response.data);
                    }
                );
            return deferred.promise;
        }

        // returns only the currently active classification
        // NOTE: the 1 isn't requesting for record #1 - it means asking for the one selected record
        function load_classification() {
            var deferred = $q.defer();
            $http.get(__env.api_url + ':' + __env.port + '/api/v2/classification/1')
                .then(
                    function(response) {
                        deferred.resolve(response.data);
                    }
                );
            return deferred.promise;
        }

        function update_classification(id) {
            var deferred = $q.defer();
            $http.put(__env.api_url + ':' + __env.port + '/api/v2/classification/' + id)
                .then(
                    function(response) {
                        deferred.resolve(response.data);
                    }
                );
            return deferred.promise;
        }
    }
})();
