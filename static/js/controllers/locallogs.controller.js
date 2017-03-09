(function () {
    'use strict';
 
    angular
        .module('app')
        .controller('Locallogs.IndexController', Controller);

    function Controller($scope, LocalLogsService) {
        var vm = this;

        initController();

        function initController() {
            console.log('[locallogs.controller:initController():14] Got here');
            get_local_logs();
        }

        function get_local_logs() {
            console.log('[locallogs.controller:get_local_logs():19] Got here');
            LocalLogsService._get_local_logs()
                .then(
                      function(results) {
                          $scope.local_logs_list = results.local_logs_list;
                      }
                    , function(err) {
                        $scope.status = 'Error loading data: ' + err.message;
                      }
                );
        }

        function get_local_log(_name) {
            LocalLogsService._get_local_logs(_name)
                .then(
                      function(results) {
                          $scope.log_content = results.log_content;
                      }
                    , function(err) {
                        $scope.status = 'Error loading data: ' + err.message;
                      }
                );
        }
    }
})();
