(function () {
    'use strict';
 
    angular
        .module('app')
        .controller('Login.IndexController', Controller);

    function Controller($scope, $location, AuthenticationService, BannerTextService) {
        var vm = this;

        vm.login = login;
        $scope.banner_text = {};

        initController();

        function initController() {
            // reset login status
            AuthenticationService.Logout();
            load_banner_text();
        };

        function load_banner_text() {
            BannerTextService
                ._get_bannertext()
                .then(
                      function(banner_text) {
                          $scope.banner_text['banner_text'] = banner_text.banner_text;

                      }
                    , function(err) {
                        $scope.status = 'Error loading data: ' + err.message;
                      }
                );
        }

        function login() {
            vm.loading = true;
            AuthenticationService.Login(vm.username, vm.password, function (result) {
                if (result === true) {
                    $location.path('/');
                } else {
                    vm.error = 'Username or password is incorrect';
                    vm.loading = false;
                }
            });
        };
    }
})();
