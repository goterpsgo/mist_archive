(function () {
    'use strict';

    var env = {};

    if (window) {
        Object.assign(env, window.__env);
    }

    angular
        .module('app', ['ui.router', 'ngMessages', 'ngStorage', 'ngAnimate', 'ngTouch', 'ui.bootstrap', 'satellizer', 'ngFileUpload'])
        .config(config)
        .constant('__env', env)
        .run(run);

    // all providers need to be defined in config()
    function config($stateProvider, $httpProvider, $urlRouterProvider, $authProvider, $locationProvider) {
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
                , '_nav' : {
                  templateUrl: 'static/html/nav.view.html',
                    controller: 'Nav.IndexController',
                    controllerAs: 'vm'
                  }
                , '_classification' : {
                  templateUrl: 'static/html/classification.view.html',
                    controller: 'Classification.IndexController',
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
                , '_nav' : {
                  templateUrl: 'static/html/nav_auth_none.view.html',
                    controller: 'Nav.IndexController',
                    controllerAs: 'vm'
                  }
                , '_classification' : {
                  templateUrl: 'static/html/classification.view.html',
                    controller: 'Classification.IndexController',
                    controllerAs: 'vm'
                  }
              }
            })
            .state('signup', {
              url: '/signup',
              views : {
                '_main' : {
                  templateUrl: 'static/html/signup.view.html',
                    controller: 'Signup.IndexController',
                    controllerAs: 'vm'
                }
                , '_nav' : {
                    templateUrl: 'static/html/nav_auth_none.view.html',
                    controller: 'Nav.IndexController',
                    controllerAs: 'vm'
                  }
                , '_classification' : {
                  templateUrl: 'static/html/classification.view.html',
                    controller: 'Classification.IndexController',
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
                , '_nav' : {
                  templateUrl: 'static/html/nav.view.html',
                    controller: 'Nav.IndexController',
                    controllerAs: 'vm'
                  }
                , '_classification' : {
                  templateUrl: 'static/html/classification.view.html',
                    controller: 'Classification.IndexController',
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
                , '_nav' : {
                  templateUrl: 'static/html/nav.view.html',
                    controller: 'Nav.IndexController',
                    controllerAs: 'vm'
                  }
                , '_classification' : {
                  templateUrl: 'static/html/classification.view.html',
                    controller: 'Classification.IndexController',
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
                , '_nav' : {
                  templateUrl: 'static/html/nav.view.html',
                    controller: 'Nav.IndexController',
                    controllerAs: 'vm'
                  }
                , '_classification' : {
                  templateUrl: 'static/html/classification.view.html',
                    controller: 'Classification.IndexController',
                    controllerAs: 'vm'
                  }
              }
            })
            .state('profile', {
              url: '/profile',
              views : {
                '_main' : {
                  templateUrl: 'static/html/profile.view.html',
                  controller: 'Profile.IndexController',
                  controllerAs: 'vm'
                }
                , '_nav' : {
                  templateUrl: 'static/html/nav.view.html',
                    controller: 'Nav.IndexController',
                    controllerAs: 'vm'
                  }
                , '_classification' : {
                  templateUrl: 'static/html/classification.view.html',
                    controller: 'Classification.IndexController',
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
                , '_nav' : {
                  templateUrl: 'static/html/nav.view.html',
                    controller: 'Nav.IndexController',
                    controllerAs: 'vm'
                  }
                , '_classification' : {
                  templateUrl: 'static/html/classification.view.html',
                    controller: 'Classification.IndexController',
                    controllerAs: 'vm'
                  }
              }
            })
            // NOTE: the entirety of the general config state defined below is still needed for nested views
            .state('config', {
              url: '/config',
              views : {
                '_main' : {
                  templateUrl: 'static/html/config.view.html',
                  controller: 'Config.IndexController',
                  controllerAs: 'vm'
                }
                , '_nav' : {
                  templateUrl: 'static/html/nav.view.html',
                    controller: 'Nav.IndexController',
                    controllerAs: 'vm'
                  }
                , '_classification' : {
                  templateUrl: 'static/html/classification.view.html',
                    controller: 'Classification.IndexController',
                    controllerAs: 'vm'
                  }
              }
            })
            // Start config nested states
            .state('config.global_parameters', {
              url: '/config.global_parameters',
              views : {
                '_main' : {
                  templateUrl: 'static/html/config.view.html',
                  controller: 'Config.IndexController',
                  controllerAs: 'vm'
                }
                , '_nav' : {
                  templateUrl: 'static/html/nav.view.html',
                    controller: 'Nav.IndexController',
                    controllerAs: 'vm'
                  }
                , '_classification' : {
                  templateUrl: 'static/html/classification.view.html',
                    controller: 'Classification.IndexController',
                    controllerAs: 'vm'
                  }
                , '_main@config' : {
                  templateUrl: 'static/html/config_global_parameters.view.html',
                    controller: 'Config.IndexController',
                    controllerAs: 'vm'
                  }
              }
            })
            .state('config.set_banner_text', {
              url: '/config.set_banner_text',
              views : {
                '_main' : {
                  templateUrl: 'static/html/config.view.html',
                  controller: 'Config.IndexController',
                  controllerAs: 'vm'
                }
                , '_nav' : {
                  templateUrl: 'static/html/nav.view.html',
                    controller: 'Nav.IndexController',
                    controllerAs: 'vm'
                  }
                , '_classification' : {
                  templateUrl: 'static/html/classification.view.html',
                    controller: 'Classification.IndexController',
                    controllerAs: 'vm'
                  }
                , '_main@config' : {
                  templateUrl: 'static/html/config_set_banner_text.view.html',
                    controller: 'Config.IndexController',
                    controllerAs: 'vm'
                  }
              }
            })
            .state('config.set_classification_level', {
              url: '/config.set_classification_level',
              views : {
                '_main' : {
                  templateUrl: 'static/html/config.view.html',
                  controller: 'Config.IndexController',
                  controllerAs: 'vm'
                }
                , '_nav' : {
                  templateUrl: 'static/html/nav.view.html',
                    controller: 'Nav.IndexController',
                    controllerAs: 'vm'
                  }
                , '_classification' : {
                  templateUrl: 'static/html/classification.view.html',
                    controller: 'Classification.IndexController',
                    controllerAs: 'vm'
                  }
                , '_main@config' : {
                  templateUrl: 'static/html/config_set_classification_level.view.html',
                    controller: 'Config.IndexController',
                    controllerAs: 'vm'
                  }
              }
            })
            .state('config.manage_security_centers', {
              url: '/config.manage_security_centers',
              views : {
                '_main' : {
                  templateUrl: 'static/html/config.view.html',
                  controller: 'Config.IndexController',
                  controllerAs: 'vm'
                }
                , '_nav' : {
                  templateUrl: 'static/html/nav.view.html',
                    controller: 'Nav.IndexController',
                    controllerAs: 'vm'
                  }
                , '_classification' : {
                  templateUrl: 'static/html/classification.view.html',
                    controller: 'Classification.IndexController',
                    controllerAs: 'vm'
                  }
                , '_main@config' : {
                  templateUrl: 'static/html/config_manage_security_centers.view.html',
                    controller: 'Config.IndexController',
                    controllerAs: 'vm'
                  }
              }
            })
            .state('config.manage_publishing_sites', {
              url: '/config.manage_publishing_sites',
              views : {
                '_main' : {
                  templateUrl: 'static/html/config.view.html',
                  controller: 'Config.IndexController',
                  controllerAs: 'vm'
                }
                , '_nav' : {
                  templateUrl: 'static/html/nav.view.html',
                    controller: 'Nav.IndexController',
                    controllerAs: 'vm'
                  }
                , '_classification' : {
                  templateUrl: 'static/html/classification.view.html',
                    controller: 'Classification.IndexController',
                    controllerAs: 'vm'
                  }
                , '_main@config' : {
                  templateUrl: 'static/html/config_manage_publishing_sites.view.html',
                    controller: 'Config.IndexController',
                    controllerAs: 'vm'
                  }
              }
            })
            .state('config.remove_tag_definitions', {
              url: '/config.remove_tag_definitions',
              views : {
                '_main' : {
                  templateUrl: 'static/html/config.view.html',
                  controller: 'Config.IndexController',
                  controllerAs: 'vm'
                }
                , '_nav' : {
                  templateUrl: 'static/html/nav.view.html',
                    controller: 'Nav.IndexController',
                    controllerAs: 'vm'
                  }
                , '_classification' : {
                  templateUrl: 'static/html/classification.view.html',
                    controller: 'Classification.IndexController',
                    controllerAs: 'vm'
                  }
                , '_main@config' : {
                  templateUrl: 'static/html/config_remove_tag_definitions.view.html',
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
                , '_nav' : {
                  templateUrl: 'static/html/nav.view.html',
                    controller: 'Nav.IndexController',
                    controllerAs: 'vm'
                  }
                , '_classification' : {
                  templateUrl: 'static/html/classification.view.html',
                    controller: 'Classification.IndexController',
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
                , '_nav' : {
                  templateUrl: 'static/html/nav.view.html',
                    controller: 'Nav.IndexController',
                    controllerAs: 'vm'
                  }
                , '_classification' : {
                  templateUrl: 'static/html/classification.view.html',
                    controller: 'Classification.IndexController',
                    controllerAs: 'vm'
                  }
              }
            });

        // $http is a service; $httpProvider is a provider to customize the global behavior of $http
        // via the $httpProvider.defaults.headers configuration object
        // https://docs.angularjs.org/api/ng/service/$http
        // https://docs.angularjs.org/api/ng/provider/$httpProvider
        // https://www.toptal.com/web/cookie-free-authentication-with-json-web-tokens-an-example-in-laravel-and-angularjs
        $httpProvider.interceptors.push(['$q', '$location', '$localStorage', '$sessionStorage',
            function ($q, $location, $localStorage, $sessionStorage) {
                return {
                   'request': function (config) {
                       config.headers = config.headers || {};
                       if ($localStorage.currentUser && $sessionStorage.currentUser) {
                           config.headers.Authorization = 'JWT ' + $localStorage.currentUser.token.split(' ').pop();
                           // console.log('[52] currentUser: ' + $sessionStorage.currentUser.username);
                       }
                       return config;
                   },
                   'response': function (response) {
                       // best practice should be using response.config.headers.Authorization, not response.data.Authorization
                       if ((typeof(response.data.Authorization) !== 'undefined') && (typeof($localStorage.currentUser) !== 'undefined')) {
                            $localStorage.currentUser.token = 'JWT ' + response.data.Authorization.split(' ').pop();
                       }
                       return response;
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
