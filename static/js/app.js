(function () {
    'use strict';

    angular
        .module('app', ['ui.router', 'ngMessages', 'ngStorage'])
        .config(config)
        .run(run);

    // all providers need to be defined in config()
    function config($stateProvider, $httpProvider, $urlRouterProvider) {
        // default route
        $urlRouterProvider.otherwise("/");

        // app routes
        $stateProvider
            .state('home', {
                url: '/',
                templateUrl: 'static/html/home/index.view.html',
                controller: 'Home.IndexController',
                controllerAs: 'vm'
            })
            .state('login', {
                url: '/login',
                templateUrl: 'static/html/login/index.view.html',
                controller: 'Login.IndexController',
                controllerAs: 'vm'
            })
            .state('signup', {
                url: '/signup',
                templateUrl: 'static/html/signup.view.html',
                controller: 'Home.IndexController',
                controllerAs: 'vm'
            })
            .state('admin', {
                url: '/admin',
                templateUrl: 'static/html/admin/index.view.html',
                controller: 'Admin.IndexController',
                controllerAs: 'vm'
            });

        // $http is a service; $httpProvider is a provider to customize the global behavior of $http
        // via the $httpProvider.defaults.headers configuration object
        // https://docs.angularjs.org/api/ng/service/$http
        // https://docs.angularjs.org/api/ng/provider/$httpProvider
        $httpProvider.interceptors.push(['$q', '$location', '$localStorage', '$sessionStorage',
            function ($q, $location, $localStorage, $sessionStorage) {
                return {
                   'request': function (config) {
                       config.headers = config.headers || {};
                       if ($localStorage.currentUser && $sessionStorage.currentUser) {
                           config.headers.Authorization = 'Bearer ' + $localStorage.currentUser.token;
                       }
                       return config;
                   },
                   'responseError': function (response) {
                       if (response.status === 401 || response.status === 403) {
                           $location.path('/login');
                       }
                       return $q.reject(response);
                   }
                };
            }
        ]);
    }

    function run($rootScope, $http, $location, $localStorage, $sessionStorage) {
        // keep user logged in after page refresh
        if ($localStorage.currentUser && $sessionStorage.currentUser) {
            $http.defaults.headers.common.Authorization = 'Bearer ' + $localStorage.currentUser.token;
        }

        // redirect to login page if not logged in and trying to access a restricted page
        $rootScope.$on('$locationChangeStart', function (event, next, current) {
            var publicPages = ['/login', '/signup'];    // add path to array if it's not to be protected
            var restrictedPage = publicPages.indexOf($location.path()) === -1;
            if (restrictedPage && !$localStorage.currentUser && !$sessionStorage.currentUser) {
                $location.path('/login');
            }
        });
    }
})();

//app.config(['$interpolateProvider', function($interpolateProvider) {
//  $interpolateProvider.startSymbol('{ng');
//  $interpolateProvider.endSymbol('ng}');
//}]);
