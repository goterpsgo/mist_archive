(function () {
    'use strict';

    angular
        .module('app')
        .factory('AuthenticationService', Service);

    function Service($http, $localStorage) {
        var service = {};

        service.Login = Login;
        service.Logout = Logout;

        return service;

        function Login(username, password, callback) {
            $http.post('/auth', { username: username, password: password })
            // var data_as_json = angular.toJson({"username": username, "password": password});
            // var headers =
            // $http.post('/auth', data_as_json)
                .success(function (response) {
                    console.log('[success]');
                    // login successful if there's a token in the response
                    if (response.data.access_token) {
                        // store username and token in local storage to keep user logged in between page refreshes
                        $localStorage.currentUser = { username: username, token: response.data.access_token };

                        // add jwt token to auth header for all requests made by the $http service
                        $http.defaults.headers.common.Authorization = 'Bearer ' + response.data.access_token;

                        // execute callback with true to indicate successful login
                        callback(true);
                    } else {
                        // execute callback with false to indicate failed login
                        callback(false);
                    }
                })
                .error(function(data, status) {
                    console.log('[ERROR] ', status, data);
                });
        }

        function Logout() {
            // remove user from local storage and clear http auth header
            delete $localStorage.currentUser;
            $http.defaults.headers.common.Authorization = '';
        }
    }
})();
(function () {
    'use strict';

    angular
        .module('app')
        .factory('AuthenticationService', Service);

    function Service($http, $localStorage) {
        var service = {};

        service.Login = Login;
        service.Logout = Logout;

        return service;

        function Login(username, password, callback) {
            $http.post('/auth', { username: username, password: password })
            // var data_as_json = angular.toJson({"username": username, "password": password});
            // var headers =
            // $http.post('/auth', data_as_json)
                .success(function (response) {
                    console.log('[success]');
                    // login successful if there's a token in the response
                    if (response.access_token) {
                        // store username and token in local storage to keep user logged in between page refreshes
                        $localStorage.currentUser = { username: username, token: response.access_token };

                        // add jwt token to auth header for all requests made by the $http service
                        $http.defaults.headers.common.Authorization = 'Bearer ' + response.access_token;

                        // execute callback with true to indicate successful login
                        callback(true);
                    } else {
                        // execute callback with false to indicate failed login
                        callback(false);
                    }
                })
                .error(function(data, status) {
                        // execute callback with false to indicate failed login
                        callback(false);
                });
        }

        function Logout() {
            // remove user from local storage and clear http auth header
            delete $localStorage.currentUser;
            $http.defaults.headers.common.Authorization = '';
        }
    }
})();
