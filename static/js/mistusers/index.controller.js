(function () {
    'use strict';
 
    angular
        .module('app')
        .controller('UserController', Controller);

    function Controller($scope, MistUsersService) {
        // $scope.my_stuff = this.get_stuff();
        // $scope.stuff = get_stuff();
        $scope.users = get_users();

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

        $scope.add_user = function() {
            console.log('Add user');
        };
    }
})();
