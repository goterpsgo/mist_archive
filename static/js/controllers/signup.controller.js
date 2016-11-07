(function () {
    'use strict';
 
    angular
        .module('app')
        .controller('Signup.IndexController', Controller);

    function Controller($scope, $location, AuthenticationService, ReposService) {
        $scope.repos;
        var vm = this;

        initController();

        function initController() {
            // reset login status
            AuthenticationService.Logout();
            get_repos();
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
        }

        $scope.add_repo = function() {
            console.log('Add repo');
        };
    }
})();
