(function () {
    'use strict';
 
    angular
        .module('app')
        .controller('Signup.IndexController', Controller);

    function Controller($location, AuthenticationService) {
        var vm = this;
            console.log('Got here');

        vm.login = login;

        initController();

        function initController() {
            // reset login status
            AuthenticationService.Logout();
        };

        function signup() {
            vm.loading = true;
            // AuthenticationService.Login(vm.username, vm.password, function (result) {
            //     if (result === true) {
            //         $location.path('/');
            //     } else {
            //         vm.error = 'Username or password is incorrect';
            //         vm.loading = false;
            //     }
            // });
        };
    }
})();
