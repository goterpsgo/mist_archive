(function () {
    'use strict';
 
    angular
        .module('app')
        .controller('UserController', Controller);

    function Controller($scope, $sessionStorage, MistUsersService) {
        if ($sessionStorage.currentUser) {
            $scope.username = $sessionStorage.currentUser.username;
            $scope.users = get_users();
        }

        // function initController() {
        // };

        function get_stuff() {
            // return 'Here\'s more stuff';
            console.log(['[17] Got here']);
            MistUsersService._get_stuff()
                .then(
                    function(stuff) {
                        $scope.stuff = stuff;
                    }
                );
        }

        function get_users() {
            MistUsersService._get_users()
                .then(
                      function(users) {
                          $scope.users = users;
                          $scope.menu_items = [];
                          users.forEach(function(u) {
                              // build $scope.menu_items collection to populate top nav menu
                              if (u.username == $scope.username) {
                                  $scope.menu_items.push({'text': 'Repos Auto Tags', 'state': 'repostag'});
                                  $scope.menu_items.push({'text': 'Assets Manual Tags', 'state': 'assetstag'});
                                  $scope.menu_items.push({'text': 'Publish', 'state': 'publish'});
                                  if (u.permission == 'Admin User' || u.permission == 'Super User') {
                                      $scope.menu_items.push({'text': 'Admin', 'state': 'admin'});
                                      $scope.menu_items.push({'text': 'Config', 'state': 'config'});
                                      $scope.menu_items.push({'text': 'Tag Activities', 'state': 'tagactivities'});
                                      $scope.menu_items.push({'text': 'Local Logs', 'state': 'locallogs'});
                                  }
                                  $scope.menu_items.push({'text': 'Logout', 'state': 'login'});
                              }
                          });
                      }
                    , function(err) {
                        $scope.status = 'Error loading data: ' + err.message;
                      }
                );
        }

        function get_user_by_id(id) {
            MistUsersService._get_user_by_id(1)
                .then(
                      function(users) {
                          $scope.user = user;
                          return user;
                      }
                    , function(err) {
                        $scope.status = 'Error loading data: ' + err.message;
                      }
                );
        }

        function get_user_by_username() {
            MistUsersService._get_user_by_username()
                .then(
                      function(users) {
                        $scope.users = users;
                      }
                    , function(err) {
                        $scope.status = 'Error loading data: ' + err.message;
                      }
                );
        }

        $scope.add_user = function() {
            console.log('Add user');
        };
    }
})();
