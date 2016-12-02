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

        $scope.repo_assign = function(user, repo, permission, has_repos) {
            var form_data = {'permission': permission, 'repo': repo, 'has_repos': has_repos};
            MistUsersService._update_user(user, form_data)
                .then(
                      function(users) {
                          $scope.users = users.users_list;
                      }
                    , function(err) {
                        $scope.status = 'Error loading data: ' + err.message;
                      }
                )
                .then(
                    function() {
                        get_users();
                    }
                );
        };

        $scope.user_admin_toggle = function(user, permission, has_repos) {
            console.log('[admin.controller:39] user_admin_toggle()');
            var form_data = {'user_admin_toggle': has_repos, 'permission': permission};
            MistUsersService._update_user(user, form_data)
                .then(
                      function(users) {
                          $scope.users = users.users_list;
                      }
                    , function(err) {
                        $scope.status = 'Error loading data: ' + err.message;
                      }
                )
                .then(
                    function() {
                        get_users();
                    }
                );
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
                .then(
                    function() {
                        get_users();
                    }
                );
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
