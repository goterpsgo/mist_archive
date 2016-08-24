(function () {
    'use strict';
 
    angular
        .module('app')
        .controller('Home.IndexController', Controller);

    function Controller($scope, MistUsersService) {
        $scope.users;
        $scope.status;
        var vm = this;

        initController();

        function initController() {
        }

        function get_users() {
            MistUsersService.get_users()
                .then(
                      function(users) {
                        $scope.users = users;
                        return users;
                      }
                    , function(err) {
                        $scope.status = 'Error loading data: ' + err.message;
                      }
                );
        }

        function get_stuff() {
            MistUsersService.get_stuff()
                .then(
                    function(stuff) {
                        return stuff;
                    }
                );
        }

        $scope.add_user = function() {
            console.log('Add user');
        };
    }
})();
