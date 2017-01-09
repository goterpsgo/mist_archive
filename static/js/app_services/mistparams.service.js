(function () {
    'use strict';

    angular
        .module('app')
        .factory('MistParamsService', Service);

    function Service($http, $q, __env) {

        var factory = {
              _load_mist_params: load_mist_params
            , _update_mist_param: update_mist_param
        };

        return factory;

        // returns list of classifications
        function load_mist_params() {
            var deferred = $q.defer();
            $http.get(__env.api_url + ':' + __env.port + '/api/v2/params')
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

        function update_mist_param(field_name, value) {
            var deferred = $q.defer();
            $http.put(__env.api_url + ':' + __env.port + '/api/v2/param/' + field_name + '/' + value)
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
