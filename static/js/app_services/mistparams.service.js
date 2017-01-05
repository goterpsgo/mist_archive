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
                );
            return deferred.promise;
        }

        function update_mist_param(field_name, value) {
            var deferred = $q.defer();
            $http.put(__env.api_url + ':' + __env.port + '/api/v2/param/' + field_name + '/' + id)
                .then(
                    function(response) {
                        deferred.resolve(response.data);
                    }
                );
            return deferred.promise;
        }
    }
})();
