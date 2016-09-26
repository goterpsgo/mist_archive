(function () {
    'use strict';

    angular
        .module('app', ['ui.router', 'ngMessages', 'ngStorage', 'ngAnimate', 'ngTouch', 'ui.bootstrap'])
        .config(config)
        .run(run);

    // all providers need to be defined in config()
    function config($stateProvider, $httpProvider, $urlRouterProvider, $locationProvider) {
        // default route
        $urlRouterProvider.otherwise("/");

        // app routes
        $stateProvider
            .state('home', {
              url: '/',
              views : {
                '_main' : {
                  templateUrl: 'static/html/home.view.html',
                    controller: 'Home.IndexController',
                    controllerAs: 'vm'
                }
              }
            })
            .state('login', {
              url: '/login',
              views : {
                '_main' : {
                  templateUrl: 'static/html/login.view.html',
                    controller: 'Login.IndexController',
                    controllerAs: 'vm'
                }
              }
            })
            .state('signup', {
              url: '/signup',
              views : {
                '_main' : {
                  templateUrl: 'static/html/signup.view.html',
                    controller: 'Home.IndexController',
                    controllerAs: 'vm'
                }
              }
            })
            .state('repostag', {
              url: '/repostag',
              views : {
                '_main' : {
                  templateUrl: 'static/html/repostag.view.html',
                    controller: 'Repostag.IndexController',
                    controllerAs: 'vm'
                }
              }
            })
            .state('assetstag', {
              url: '/assetstag',
              views : {
                '_main' : {
                  templateUrl: 'static/html/assetstag.view.html',
                    controller: 'Assetstag.IndexController',
                    controllerAs: 'vm'
                }
              }
            })
            .state('publish', {
              url: '/publish',
              views : {
                '_main' : {
                  templateUrl: 'static/html/publish.view.html',
                  controller: 'Publish.IndexController',
                  controllerAs: 'vm'
                }
              }
            })
            .state('admin', {
              url: '/admin',
              views : {
                '_main' : {
                  templateUrl: 'static/html/admin.view.html',
                  controller: 'Admin.IndexController',
                  controllerAs: 'vm'
                }
              }
            })
            .state('config', {
              url: '/config',
              views : {
                '_main' : {
                  templateUrl: 'static/html/config.view.html',
                  controller: 'Config.IndexController',
                  controllerAs: 'vm'
                }
              }
            })
            .state('tagactivities', {
              url: '/tagactivities',
              views : {
                '_main' : {
                  templateUrl: 'static/html/tagactivities.view.html',
                  controller: 'Tagactivities.IndexController',
                  controllerAs: 'vm'
                }
              }
            })
            .state('locallogs', {
              url: '/locallogs',
              views : {
                '_main' : {
                  templateUrl: 'static/html/locallogs.view.html',
                  controller: 'Locallogs.IndexController',
                  controllerAs: 'vm'
                }
              }
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
                           config.headers.Authorization = 'JWT ' + $localStorage.currentUser.token;
                           // console.log('[52] currentUser: ' + $sessionStorage.currentUser.username);
                       }
                       return config;
                   },
                   'responseError': function (response) {
                       console.log('[status] ' + response.status);
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
            $http.defaults.headers.common.Authorization = 'JWT ' + $localStorage.currentUser.token;
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
