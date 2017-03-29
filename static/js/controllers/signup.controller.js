(function () {
    'use strict';
 
    angular
        .module('app')
        .controller('Signup.IndexController', Controller);

    function Controller($scope, $location, AuthenticationService, ReposService, MistUsersService, SubjectDNService) {
        $scope.repos = '';
        $scope.result;
        $scope.alert_class = '';
        $scope.response_message = '';
        $scope.status = '';
        $scope._user = {};

        $scope.submit_signup = function() {
            return MistUsersService._signup_user($scope._user)
                .then(function(result) {
                    $scope.response_message = result.response.message;
                    $scope.result = result.response.result;
                    $scope.class = result.response.class;
            });
        }
        var vm = this;

        initController();

        function initController() {
            // reset login status
            AuthenticationService.Logout();
            get_repos();
            get_subjectdn();
        }

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

        function get_subjectdn() {
            SubjectDNService
                ._get_subjectdn()
                .then(
                      function(result) {
                          console.log(result.subject_dn);
                          $scope._user.subject_dn = result.subject_dn;
                          console.log(result.subject_dn);
                      }
                    , function(err) {
                        $scope.status = 'Error loading data: ' + err.message;
                      }
                )
        }
    }
})();
