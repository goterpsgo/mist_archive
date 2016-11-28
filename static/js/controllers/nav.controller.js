(function () {
    'use strict';
 
    angular
        .module('app')
        .controller('Nav.IndexController', Controller);

    function Controller($scope, $localStorage, MistUsersService) {
        $scope.users;
        $scope.status;
        $scope.user;
        var vm = this;

        initController();

        function initController() {
            if (typeof $localStorage.currentUser != 'undefined') {

                // populate $scope.user to provide user status and state to be used in the nav view.
                var username = $localStorage.currentUser.username;
                MistUsersService._get_user(username)
                    .then(
                          function(user) {
                              $scope.user = user.users_list[0];
                          }
                        , function(err) {
                            $scope.status = 'Error loading data: ' + err.message;
                          }
                    );
            }
        }
    }
})();
