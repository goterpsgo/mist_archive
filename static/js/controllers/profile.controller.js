(function () {
    'use strict';
 
    angular
        .module('app')
        .controller('Profile.IndexController', Controller);

    function Controller($scope, MistUsersService, ReposService, $localStorage, $timeout) {
        var vm = this;
        $scope.profile = {};
        $scope.repos = {};

        initController();

        function initController() {
            get_this_user();

            // Delay get_users() by 1ms to not overwhelm the database (unless there's a better solution - JWT 6 Dec 2016)
            $timeout(function() {
                get_repos();
            }, 1);
        }

        function get_this_user() {
            var username = $localStorage.currentUser.username;
            MistUsersService._get_user(username)
                .then(
                      function(user) {
                          $scope.profile = user.users_list[0];
                          console.log(user.users_list[0]);
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
                      }
                    , function(err) {
                        $scope.status = 'Error loading data: ' + err.message;
                      }
                );
        };
    }
})();
