// code based on http://jasonwatmore.com/post/2016/04/05/AngularJS-JWT-Authentication-Example-Tutorial.aspx
(function () {
    'use strict';

    angular
        .module('app')
        .factory('AuthenticationService', Service);

    function Service($http, $localStorage, $sessionStorage) {
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
                    // login successful if there's a token in the response
                    // code below based on http://www.redotheweb.com/2015/11/09/api-security.html
                    if (response.access_token) {
                        // store username and token in local storage to keep user logged in between page refreshes
                        // for handling CSRF
                        $localStorage.currentUser = { username: username, token: response.access_token };

                        // add jwt token to auth header for all requests made by the $http service
                        $http.defaults.headers.common.Authorization = 'JWT ' + response.access_token;

                        // add token to session
                        // for handling XSS
                        $sessionStorage.currentUser = { username: username, token: response.access_token };

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
            // remove user from session
            delete $sessionStorage.currentUser;
            $http.defaults.headers.common.Authorization = '';
        }
    }
})();
