(function () {
    'use strict';
 
    angular
        .module('app')
        .controller('Admin.IndexController', Controller);

    function Controller($scope, $localStorage, MistUsersService, ReposService) {
        $scope.users;   // may not be needed...
        $scope.assign_repos;
        var vm = this;

        initController();

        function initController() {
            get_repos();
            get_users();
        }

        $scope.repo_assign = function(user, repo, permission, cnt_repos) {
            var form_data = {'permission': permission, 'repo': repo, 'cnt_repos': cnt_repos};
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

        $scope.user_admin_toggle = function(user, permission, cnt_repos) {
            console.log('[admin.controller:39] user_admin_toggle()');
            var form_data = {'user_admin_toggle': cnt_repos, 'permission': permission};
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
        };

        function get_repos() {
            ReposService._get_repos()
                .then(
                      function(repos) {
                          $scope.assign_repos = repos.repos_list;
                      }
                    , function(err) {
                        $scope.status = 'Error loading data: ' + err.message;
                      }
                );
        };
    }
})();
