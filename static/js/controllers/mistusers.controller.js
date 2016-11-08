(function () {
    'use strict';
 
    angular
        .module('app')
        .controller('MistController', Controller);

    function Controller($scope, $sessionStorage, MistUsersService) {

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
            MistUsersService._get_user(id)
                .then(
                      function(user) {
                          $scope.user = user.users_list[0];
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
