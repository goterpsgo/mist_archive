(function () {
    'use strict';
 
    angular
        .module('app')
        .controller('Admin.IndexController', Controller);

    function Controller($scope, $localStorage, MistUsersService, ReposService, $timeout) {
        $scope.users;   // may not be needed...
        $scope.assign_repos;
        $scope.check_all = false;
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
            console.log('[25] Got here');
            // var form_data = {'permission': permission, 'repo': repo, 'cnt_repos': cnt_repos};
            // MistUsersService._update_user(user, form_data)
            //     .then(
            //           function(users) {
            //               $scope.users = users.users_list;
            //           }
            //         , function(err) {
            //             $scope.status = 'Error loading data: ' + err.message;
            //           }
            //     )
            //     .then(
            //         function() {
            //             get_users();
            //         }
            //     );
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

        $scope.check_all_repos = function() {
            if ($scope.check_all) {
                $scope.check_all = false;
            }
            else {
                $scope.check_all = true;
            }
            angular.forEach($scope.assign_repos, function(repo) {
                repo.Checked = $scope.check_all;
            })
        };
    }
})();
