(function () {
    'use strict';
 
    angular
        .module('app')
        .controller('Admin.IndexController', Controller);

    function Controller($scope, $localStorage, MistUsersService) {
        $scope.users;   // may not be needed...
        $scope.foo = 'bar';
        var vm = this;

        initController();

        function initController() {
            get_users();
        }

        $scope.repo_assign = function(user, repo) {
            get_users();
        };

        $scope.delete_user = function(user) {
            MistUsersService._delete_user(user)
                .then(
                      function(users) {
                          $scope.users = users.users_list;
                      }
                    , function(err) {
                        $scope.status = 'Error loading data: ' + err.message;
                      }
                )
            get_users();
        };

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
    }
})();
