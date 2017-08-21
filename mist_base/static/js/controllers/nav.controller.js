(function () {
    'use strict';
 
    angular
        .module('app')
        .controller('Nav.IndexController', Controller);

    function Controller($scope, $localStorage, MistUsersService, AuthenticationService, $location) {
        $scope.users;   // may not be needed...
        $scope.status;
        $scope.user;
        $scope.selectedTab = '';
        var vm = this;
        vm.login = login;

        initController();

        function initController() {
            get_this_user();
        }

        function get_this_user() {
            // populate $scope.user to provide user status and state to be used in the nav view.
            if ($localStorage.currentUser !== undefined) {
                // Cache results in $localStorage to minimize calls to database-driven RESTful endpoint
                if (($localStorage.user === undefined) || ($scope.user === undefined)) {
                    var username = $localStorage.currentUser.username;
                    MistUsersService._get_user(username)
                        .then(
                              function(user) {
                                  $localStorage.user = user.users_list[0];
                                  $scope.user = user.users_list[0];
                              }
                            , function(err) {
                                $scope.status = 'Error loading data: ' + err.message;
                              }
                        );
                }

                // populate $scope.user to provide user status and state to be used in the nav view.
                // $scope.user = $localStorage.user;
            }
        }

        function login() {
            vm.loading = true;
            AuthenticationService.Login(vm.username, vm.password, function (result) {
                if (result === true) {
                    $location.path('/');
                } else {
                    vm.error = 'Username or password is incorrect. Accounts are locked after three (3) failed attempts.';
                    vm.loading = false;
                }
            });
        };
    }
})();
