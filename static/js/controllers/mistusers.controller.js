(function () {
    'use strict';
 
    angular
        .module('app')
        .controller('UserController', Controller);

    function Controller($scope, $sessionStorage, MistUsersService) {

        initController();

        function initController() {
            if ($sessionStorage.currentUser) {
                get_user_by_username($sessionStorage.currentUser.username);
            }
        };

        function get_stuff() {
            // return 'Here\'s more stuff';
            MistUsersService._get_stuff()
                .then(
                    function(stuff) {
                        $scope.stuff = stuff;
                    }
                );
        }

        function get_users() {
            MistUsersService._get_users()
                .then(
                      function(users) {
                          $scope.users = users;
                      }
                    , function(err) {
                        $scope.status = 'Error loading data: ' + err.message;
                      }
                );
        }

        function get_user_by_id(id) {
            MistUsersService._get_user_by_id(id)
                .then(
                      function(user) {
                          $scope.user = user;
                      }
                    , function(err) {
                        $scope.status = 'Error loading data: ' + err.message;
                      }
                );
        }

        function get_user_by_username(username) {
            MistUsersService._get_user_by_username(username)
                .then(
                      function(user) {
                            $scope.user = user;
                      }
                    , function(err) {
                        $scope.status = 'Error loading data: ' + err.message;
                      }
                );
        }

        $scope.add_user = function() {
            console.log('Add user');
        };
    }
})();
