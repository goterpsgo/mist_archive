(function () {
    'use strict';

    angular
        .module('app')
        .factory('AssetsService', Service);

    function Service($http, $q, __env) {
        var factory = {
              _get_assets: get_assets
            , _get_tagged_assets: get_tagged_assets
            , _insert_taggedassets: insert_taggedassets
            , _delete_asset_tag: delete_asset_tag
        };

        return factory;

        // get_assets should use $http.get() but won't handle multi-field structured data - JWT 15 Feb 2017
        function get_tagged_assets(_params) {

            var deferred = $q.defer();

            $http.get(__env.api_url + ':' + __env.port + '/api/v2/assets')
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

        // get_assets should use $http.get() but won't handle multi-field structured data - JWT 15 Feb 2017
        function get_assets(_params) {

            var deferred = $q.defer();
            var config = {
                headers : {
                    'Content-Type': 'application/json;charset=utf-8;'
                }
            }

            var form_data = {'action': 'search_assets'};    // form_data will always have a minimum size of 1 - JWT 15 Feb 2017
            if (_params.search_value !== undefined) {
                form_data.search_value = _params.search_value;
            }
            if (_params.category !== undefined) {
                form_data.category = _params.category.value;
            }
            if (_params.repo !== undefined) {
                form_data.repo_id = _params.repo.repo_id;
                form_data.sc_id = _params.repo.sc_id;
            }

            $http.post(__env.api_url + ':' + __env.port + '/api/v2/assets', form_data, config)
                .then(
                    function(response) {
                        deferred.resolve(response.data);
                    }
                    , function(data, status, headers, config) {
                        // deferred.resolve(response.data.response);
                        deferred.resolve(JSON.parse('{"response": {"method": "POST", "result": "error", "status": "' + status + '"}}'));
                    }
                );
            return deferred.promise;
        }

        function insert_taggedassets(form_data) {
            var deferred = $q.defer();
            var config = {
                headers : {
                    'Content-Type': 'application/json;charset=utf-8;'
                }
            }

            form_data['action'] = 'tag_assets';    // form_data will always have a minimum size of 1 - JWT 15 Feb 2017
            $http.post(__env.api_url + ':' + __env.port + '/api/v2/assets', form_data, config)
                .then(function(response) {
                    deferred.resolve(response.data);
                }
                , function(data, status, headers, config) {
                    // deferred.resolve(response.data.response);
                    deferred.resolve(JSON.parse('{"response": {"method": "POST", "result": "error", "status": "' + status + '"}}'));
                });
            return deferred.promise;
        }

        function delete_asset_tag(_id) {
            var deferred = $q.defer();

            $http.delete(__env.api_url + ':' + __env.port + '/api/v2/assets/' + _id)
                .then(function(result) {
                    deferred.resolve(result.data);
                }
                , function(data, status, headers, config) {
                    // deferred.resolve(response.data.response);
                    deferred.resolve(JSON.parse('{"response": {"method": "DELETE", "result": "error", "status": "' + status + '"}}'));
                });
            return deferred.promise;
        }
    }
})();
