(function () {
    'use strict';
 
    angular
        .module('app')
        .controller('Repos.IndexController', Controller);

    function Controller($scope, $sessionStorage, ReposService) {
        $scope.repos;
        var vm = this;

        // initController();
        //
        // function initController() {
        // };

        function get_repos() {
            MistUsersService._get_repos()
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
