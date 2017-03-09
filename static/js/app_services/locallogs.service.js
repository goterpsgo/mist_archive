(function () {
    'use strict';

    angular
        .module('app')
        .factory('BannerTextService', Service);

    function Service($http, $q, __env) {
        var factory = {
              _get_bannertext: get_bannertext
            , _insert_bannertext: insert_bannertext
            , _delete_bannertext: delete_bannertext
        };

        return factory;

        function get_bannertext() {
            var deferred = $q.defer();
            $http.get(__env.api_url + ':' + __env.port + '/api/v2/bannertext')
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

        function insert_bannertext(form_data) {
            var deferred = $q.defer();
            var config = {
                headers : {
                    'Content-Type': 'application/json;charset=utf-8;'
                }
            }

            $http.post(__env.api_url + ':' + __env.port + '/api/v2/bannertext', form_data, config)
                .then(function(form_data, status, headers, config) {
                    deferred.resolve(form_data);
                }
                , function(data, status, headers, config) {
                    deferred.resolve(JSON.parse('{"response": {"method": "POST", "result": "error", "status": "' + status + '"}}'));
                })
            ;
            return deferred.promise;
        }

        function delete_bannertext() {
            var deferred = $q.defer();
            var config = {
                headers : {
                    'Content-Type': 'application/json;charset=utf-8;'
                }
            };

            $http.delete(__env.api_url + ':' + __env.port + '/api/v2/bannertext')
                .then(function(data, status, headers) {
                    deferred.resolve(data);
                }
                , function(data, status, header, config) {
                    deferred.resolve(JSON.parse('{"response": {"method": "DELETE", "result": "error", "status": "' + status + '"}}'));
                }
            );
            return deferred.promise;
        }
    }
})();
