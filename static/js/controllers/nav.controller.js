(function () {
    'use strict';
 
    angular
        .module('app')
        .controller('Nav.IndexController', Controller);

    function Controller($scope, $localStorage, MistUsersService) {
        $scope.users;   // may not be needed...
        $scope.status;
        $scope.user;
        var vm = this;

        initController();

        function initController() {
            if (typeof $localStorage.currentUser !== 'undefined') {
                // Cache results in $localStorage to minimize calls to database-driven RESTful endpoint
                if (typeof $localStorage.user === 'undefined') {
                    var username = $localStorage.currentUser.username;
                    MistUsersService._get_user(username)
                        .then(
                              function(user) {
                                  console.log(user.users_list[0]);
                                  $localStorage.user = user.users_list[0];
                                  $scope.user = user.users_list[0];
                              }
                            , function(err) {
                                $scope.status = 'Error loading data: ' + err.message;
                              }
                        );
                }

                // populate $scope.user to provide user status and state to be used in the nav view.
                $scope.user = $localStorage.user;
            }
        }
    }
})();
