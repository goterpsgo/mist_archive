(function () {
    'use strict';

    var env = {};

    // code to handle MSIE since it doesn't support Object.assign()
    if (typeof Object.assign != 'function') {
      Object.assign = function(target) {
        'use strict';
        if (target == null) {
          throw new TypeError('Cannot convert undefined or null to object');
        }

        target = Object(target);
        for (var index = 1; index < arguments.length; index++) {
          var source = arguments[index];
          if (source != null) {
            for (var key in source) {
              if (Object.prototype.hasOwnProperty.call(source, key)) {
                target[key] = source[key];
              }
            }
          }
        }
        return target;
      };
    }

    if (window) {
        Object.assign(env, window.__env);
    }

    angular
        .module('app', ['ui.router', 'ngCookies', 'ngMessages', 'ngStorage', 'ngAnimate', 'ngTouch', 'ui.bootstrap', 'satellizer', 'ngFileUpload', 'webix', 'ngMaterial', 'ui.grid', 'ngFileSaver'])
        .config(config)
        .constant('__env', env)
        .run(run);

    // all providers need to be defined in config()
    function config($stateProvider, $httpProvider, $urlRouterProvider, $authProvider, $locationProvider) {

        // You can also use regex for the match parameter
        // Use /publish.list as default landing page when user tries to access /
        $urlRouterProvider.when('/?', '/publish/publish.list');

        // default route for all un-authenticated browsers
        $urlRouterProvider.otherwise("/login");

        // app routes
        $stateProvider
            // .state('home', {
            //   url: '/',
            //   views : {
            //       '_main' : {
            //       templateUrl: 'static/html/home.view.html',
            //         controller: 'Home.IndexController',
            //         controllerAs: 'vm'
            //       }
            //     , '_nav' : {
            //       templateUrl: 'static/html/nav.view.html',
            //         controller: 'Nav.IndexController',
            //         controllerAs: 'vm'
            //       }
            //     , '_classification' : {
            //       templateUrl: 'static/html/classification.view.html',
            //         controller: 'Classification.IndexController',
            //         controllerAs: 'vm'
            //       }
            //   }
            // })
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
            // Start config nested states
            .state('publish.list', {
              url: '/publish.list',
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
                , '_main@publish' : {
                  templateUrl: 'static/html/publish_list.view.html',
                    controller: 'Publish.IndexController',
                    controllerAs: 'vm'
                  }
              }
            })
            .state('publish.on_demand', {
              url: '/publish.on_demand',
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
                , '_main@publish' : {
                  templateUrl: 'static/html/publish_on_demand.view.html',
                    controller: 'Publish.IndexController',
                    controllerAs: 'vm'
                  }
              }
            })
            .state('publish.last_dates', {
              url: '/publish.last_dates',
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
                , '_main@publish' : {
                  templateUrl: 'static/html/publish_last_dates.view.html',
                    controller: 'Publish.IndexController',
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
            .state('config.manage_publish_sites', {
              url: '/config.manage_publish_sites',
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
                  templateUrl: 'static/html/config_manage_publish_sites.view.html',
                    controller: 'Config.IndexController',
                    controllerAs: 'vm'
                  }
              }
            })
            .state('config.manage_tag_definitions', {
              url: '/config.manage_tag_definitions',
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
                  templateUrl: 'static/html/config_manage_tag_definitions.view.html',
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
        $httpProvider.interceptors.push(['$cookies', '$q', '$location', '$localStorage', '$sessionStorage',
            function ($cookies, $q, $location, $localStorage, $sessionStorage) {
                return {
                   'request': function (config) {
                       config.headers = config.headers || {};

                       if (config.data !== undefined) {
                           if ($cookies.get('attempts') === undefined) {
                               var _expire_date = new Date();
                               _expire_date.setMinutes(_expire_date.getMinutes() + 20);
                               $cookies.put('attempts', 0,{expiry: _expire_date});
                           }

                           if ($cookies.get('attempts') !== undefined) {
                               config.headers.attempts = $cookies.get('attempts');
                               if ($cookies.get('attempts') >= 3) {
                                   $cookies.remove('attempts');
                               }
                           }
                       }

                       if ($localStorage.currentUser && $sessionStorage.currentUser) {
                           config.headers.Authorization = 'JWT ' + $localStorage.currentUser.token.split(' ').pop();
                           // console.log('[52] currentUser: ' + $sessionStorage.currentUser.username);
                       }
                       return config;
                   },
                   'response': function (response) {
                       // best practice should be using response.headers('Authorization'), not response.data.Authorization
                       if ((typeof(response.data.Authorization) !== 'undefined') && (typeof($localStorage.currentUser) !== 'undefined')) {
                            $localStorage.currentUser.token = 'JWT ' + response.data.Authorization.split(' ').pop();
                            $cookies.remove('attempts');
                       }
                       return response;
                   },
                   'responseError': function (response) {
                       if (response.config.data !== undefined) {
                           // Do not tick attempts counter if status is due to system error
                           if (($cookies.get('attempts') !== undefined) && (response.status !== 502)) {
                               $cookies.put('attempts', parseInt($cookies.get('attempts')) + 1);
                           }
                       }

                       if (response.status === 401 || response.status === 403) {
                           $location.path('/#/login');
                       }
                       return $q.reject(response);
                   }
                };
            }
        ]);
    }

    function run($rootScope, $http, $location, $localStorage, $sessionStorage, $timeout) {
        // keep user logged in after page refresh
        if ($localStorage.currentUser && $sessionStorage.currentUser) {
            $http.defaults.headers.common.Authorization = 'JWT ' + $localStorage.currentUser.token;
        }

        // redirect to login page if not logged in and trying to access a restricted page
        $rootScope.$on('$locationChangeStart', function (event, next, current) {
            var publicPages = ['', '/', '/login', '/signup'];    // add path to array if it's not to be protected
            console.log('location: ' + $location.path());
            var restrictedPage = publicPages.indexOf($location.path()) === -1;
            if (restrictedPage && !$localStorage.currentUser && !$sessionStorage.currentUser) {

                // first try to log in with pki, if haven't tried that yet
                console.log('PKI attempted previously: ' + $localStorage.authWithCertAttempted);
                if (!$localStorage.authWithCertAttempted) {
                    console.log('attempting');
                    $http.post('/auth', { username: 'xxx', password: 'xxx' })
                        .success(function (response) {
                            if (response.access_token && response.username) {
                                console.log('success callback');
                                $localStorage.authWithCertAttempted = true;
                                $localStorage.currentUser = {
                                      username: response.username,
                                      token: response.access_token
                                };

                                // add jwt token to auth header for all requests made by the $http service
                                $http.defaults.headers.common.Authorization = 'JWT ' + response.access_token;

                                // add token to session
                                $sessionStorage.currentUser = { username: response.username, token: response.access_token };
                                console.log('logged in with user ' + response.username)
                            } else {
                                console.log('error callback');
                                $localStorage.authWithCertAttempted = true;
                                if ($location.path() != '/login') {
                                    console.log('Redirect to /login');
                                    $timeout(function() {
                                        $location.path('/login');
                                    }, 100);
                                }
                            }
                        })
                        .error(function(data, status) {
                            console.log('error callback');
                            $localStorage.authWithCertAttempted = true;
                            if ($location.path() != '/login') {
                                console.log('Redirect to /login');
                                $timeout(function() {
                                    $location.path('/login');
                                }, 100);
                            }
                        });
                }
                else {
                    delete $localStorage.authWithCertAttempted;
                    delete $sessionStorage.authWithCertAttempted;
                    console.log($localStorage.authWithCertAttempted);
                    if ($location.path() != '/login') {
                        console.log('Redirect to /login');
                        $timeout(function() {
                            delete $localStorage.currentUser;
                            delete $localStorage.user;
                            $location.path('/login');
                        }, 100);
                    }
                }
            }
            // else {
            //     console.log($localStorage.authWithCertAttempted);
            //     $location.path('/login');
            // }
        });
    }
})();

//app.config(['$interpolateProvider', function($interpolateProvider) {
//  $interpolateProvider.startSymbol('{ng');
//  $interpolateProvider.endSymbol('ng}');
//}]);
