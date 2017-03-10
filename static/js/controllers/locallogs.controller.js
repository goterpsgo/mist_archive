(function () {
    'use strict';
 
    angular
        .module('app')
        .controller('Locallogs.IndexController', Controller);

    function Controller($scope, LocalLogsService) {
        var vm = this;

        initController();

        function initController() {
            get_local_logs();
        }

        function get_local_logs() {
            LocalLogsService._get_local_logs()
                .then(
                      function(results) {
                          $scope.local_logs_list = results.local_logs_list;
                          $scope.id_to_path_map = results.id_to_path_map;
                      }
                    , function(err) {
                        $scope.status = 'Error loading data: ' + err.message;
                      }
                );
        }

        this.node_click = function(_id) {
            if ($scope.id_to_path_map[_id] !== undefined) {
                LocalLogsService._get_local_log($scope.id_to_path_map[_id])
                    .then(
                          function(results) {
                              $scope.log_content = results.log_content.content;
                          }
                        , function(err) {
                            $scope.status = 'Error loading data: ' + err.message;
                          }
                    );
            }
        }
    }
})();
