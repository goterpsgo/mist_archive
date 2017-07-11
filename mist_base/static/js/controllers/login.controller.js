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
            vm.loading = true;
            BannerTextService
                ._get_bannertext()
                .then(
                      function(banner_text) {
                          if (banner_text.banner_text.length > 0) {
                            $scope.banner_text['banner_text'] = banner_text.banner_text;
                          }
                          else {
                              $scope.banner_text['banner_text'] = 'Unauthorized access is prohibited.';
                          }
                          vm.loading = false;
                      }
                    , function(err) {
                          $scope.status = 'Error loading data: ' + err.message;
                          vm.loading = false;
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
