(function () {
    'use strict';
 
    angular
        .module('app')
        .controller('Profile.IndexController', Controller);

    function Controller($scope, MistUsersService, ReposService, $localStorage, $timeout) {
        var vm = this;
        $scope.profile = {};
        $scope.repos = {};
        $scope.status = '';
        $scope.status_class = '';

        initController();

        function initController() {
            get_this_user();

            // Delay get_users() by 1ms to not overwhelm the database (unless there's a better solution - JWT 6 Dec 2016)
            $timeout(function() {
                get_repos();
            }, 10);
        }

        function get_this_user() {
            var username = $localStorage.currentUser.username;
            MistUsersService._get_user(username)
                .then(
                      function(user) {
                          $scope.profile = user.users_list[0];

                          // if there are assigned repos for given user, add .repos[] entries to bound .assign_repos array for dropdown selections
                          if (Object.keys($scope.profile.repos).length > 0) {
                              $scope.profile.assign_repos = [];
                              angular.forEach($scope.profile.repos, function(repo, key) {
                                  var selected_repo_entry = {'repo_id': repo.repoID, 'sc_id': repo.scID};
                                  $scope.profile.assign_repos.push(selected_repo_entry);
                              })
                          }
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
                          $scope.repos = repos.repos_list;

                          if (repos.response !== undefined) {
                              // display a status message to user
                              $scope.status = '[get_repos()] ' + repos.response.message;
                              $scope.status_class = repos.response.class;

                              // clear status message after five seconds
                              $timeout(function() {
                                  $scope.status = '';
                                  $scope.status_class = '';
                              }, 5000);
                          }
                      }
                    , function(err) {
                        $scope.status = 'Error loading data: ' + err.message;
                      }
                );
        };

        $scope.update_user_profile = function(_id) {

            // convert assign_repos into repo_id,sc_id string
            for (var cnt in $scope.profile.assign_repos) {
                var repo = $scope.profile.assign_repos[cnt];
                $scope.profile.assign_repos[cnt] = repo['repo_id'] + ',' + repo['sc_id'];
            }

            $scope.profile.assign_submit = $localStorage.user.permission;   // whether or not user who submits form is user (0,1) or admin (2,3)
            MistUsersService._update_user(_id, $scope.profile)
                .then(function(result) {
                    // display a status message to user
                    $scope.status = result.data.response.message;
                    $scope.status_class = result.data.response.class;

                    get_this_user();    // retrieve this user's properties to rehighlight selected repos in dropdown list

                    // if there are assigned repos for given user, add .repos[] entries to bound .assign_repos array for dropdown selections
                    if (Object.keys($scope.profile.repos).length > 0) {
                        $scope.profile.assign_repos = [];
                        angular.forEach($scope.profile.repos, function(repo, key) {
                            var selected_repo_entry = {'repo_id': repo.repoID, 'sc_id': repo.scID};
                            $scope.profile.assign_repos.push(selected_repo_entry);
                        })
                    }
                })
                .then(function() {
                    // clear status message after five seconds
                    $timeout(function() {
                        $scope.status = '';
                        $scope.status_class = '';
                    }, 5000).then(function() {
                        // load_sc_data();
                    });
                });
        };
    }
})();
