(function () {
    'use strict';
 
    angular
        .module('app')
        .controller('Admin.IndexController', Controller);

    function Controller($scope, $localStorage, MistUsersService, ReposService, $timeout) {
        $scope.users;   // may not be needed...
        $scope.assign_repos;
        $scope.check_all_repos_state = false;
        $scope._repo = {}
        $scope._form_fields = {}
        var vm = this;

        initController();

        function initController() {
            // load_page_data();
            get_repos();
            // Delay get_users() by 1ms to not overwhelm the database (unless there's a better solution - JWT 6 Dec 2016)
            $timeout(function() {
                get_users();
            }, 1);
        }

        $scope.submit_assign_repos = function() {
            // var form_data = {'permission': permission, 'repo': repo, 'cnt_repos': cnt_repos};

            var arr_user = $scope._form_fields.assign_user.split(',');
            $scope._form_fields.id = arr_user[0];
            $scope._form_fields.username = arr_user[1];
            $scope._form_fields.permission = arr_user[2];
            $scope._form_fields.assign_submit = $localStorage.user.permission;  // whether or not user who submits form is user (0,1) or admin (2,3)
            delete $scope._form_fields['assign_user'];

            MistUsersService
                ._update_user($scope._form_fields.id, $scope._form_fields)
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
                        $scope._form_fields = {};
                    }
                );
        };

        $scope.repo_assign = function(user, repo, permission, cnt_repos) {
            var form_data = {'permission': permission, 'repo': repo, 'cnt_repos': cnt_repos};
            MistUsersService
                ._update_user(user, form_data)
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

        function load_page_data() {
            MistUsersService
                ._get_users()
                .then(
                      function(users) {
                          $scope.users = users.users_list;
                      }
                    , function(err) {
                        $scope.status = 'Error loading data: ' + err.message;
                      }
                )
                .then(
                    ReposService
                        ._get_repos()
                        .then(
                              function(repos) {
                                  $scope.assign_repos = repos.repos_list;
                              }
                            , function(err) {
                                $scope.status = 'Error loading data: ' + err.message;
                              }
                        )
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
        }

        $scope.check_all_repos = function() {
            $scope.check_all_repos_state = (($scope.check_all_repos_state) ? false : true);
            angular.forEach($scope.assign_repos, function(repo) {
                repo.Checked = $scope.check_all_repos_state;
            })
        };


        $scope.toggle_enable = function(user, permission, switch_to) {
            var form_data = {'lockout': switch_to};
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
        }

        $scope.refresh_data = function() {
            get_repos();
        };
    }
})();
