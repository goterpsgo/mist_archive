(function () {
    'use strict';
 
    angular
        .module('app')
        .controller('UserController', Controller);

    function Controller($scope, $sessionStorage, MistUsersService) {
        // $scope.my_stuff = this.get_stuff();
        // $scope.stuff = get_stuff();
        $scope.users = get_users();
        $scope.username = $sessionStorage.currentUser.username;
        // $scope.user = get_user_by_id(1);

        // function initController() {
        // };

        function get_stuff() {
            // return 'Here\'s more stuff';
            console.log(['[17] Got here']);
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
            MistUsersService._get_user_by_id(1)
                .then(
                      function(users) {
                          $scope.user = user;
                          return user;
                      }
                    , function(err) {
                        $scope.status = 'Error loading data: ' + err.message;
                      }
                );
        }

        function get_user_by_username() {
            MistUsersService._get_user_by_username()
                .then(
                      function(users) {
                        $scope.users = users;
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
