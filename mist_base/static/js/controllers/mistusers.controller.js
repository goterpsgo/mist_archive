(function () {
    'use strict';
 
    angular
        .module('app')
        .controller('MistController', Controller);

    function Controller($scope, $sessionStorage, $localStorage, MistUsersService) {

        initController();

        function initController() {
            if ($sessionStorage.currentUser) {
                get_user($sessionStorage.currentUser.username);
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
                          $scope.users = users.users_list;
                      }
                    , function(err) {
                        $scope.status = 'Error loading data: ' + err.message;
                      }
                );
        }

        function get_user(id) {
            // Cache results in $localStorage to minimize calls to database-driven RESTful endpoint
            if (typeof $localStorage.user === 'undefined') {
                // populate $scope.user to provide user status and state to be used in the nav view.
                MistUsersService._get_user(id)
                    .then(
                          function(user) {
                              $localStorage.user = user.users_list[0];
                              $scope.user = user.users_list[0];
                          }
                        , function(err) {
                            $scope.status = 'Error loading data: ' + err.message;
                          }
                    );
            }

            // populate $scope.user to provide user status and state to be used in the nav view.
            $scope.user = $localStorage.user;
        }
    }
})();
