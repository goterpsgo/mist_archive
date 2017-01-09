(function () {
    'use strict';

    angular
        .module('app')
        .factory('ClassificationService', Service);

    function Service($http, $q, __env) {
        var classes = [];
        classes['None'] = '';
        classes['Unclassified'] = 'bg-unclassified';
        classes['Confidential'] = 'bg-confidential';
        classes['Secret'] = 'bg-secret';
        classes['Top Secret'] = 'bg-top-secret';
        classes['Top Secret - No Foreign'] = 'bg-tssci';

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
                        for (var i in response.data.classifications_list) {
                            response.data.classifications_list[i].class = classes[response.data.classifications_list[i].level];
                        }
                        deferred.resolve(response.data);
                    }
                    , function(data, status, headers, config) {
                        deferred.resolve(JSON.parse('{"response": {"method": "GET", "result": "error", "status": "' + status + '"}}'));
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
                        response.data.classifications_list[0].class = classes[response.data.classifications_list[0].level];
                        deferred.resolve(response.data);
                    }
                    , function(data, status, headers, config) {
                            // deferred.resolve(response.data.response);
                        deferred.resolve(JSON.parse('{"response": {"method": "GET", "result": "error", "status": "' + status + '"}}'));
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
                    , function(data, status, headers, config) {
                        // deferred.resolve(response.data.response);
                        deferred.resolve(JSON.parse('{"response": {"method": "PUT", "result": "error", "status": "' + status + '"}}'));
                    }
                );
            return deferred.promise;
        }
    }
})();
