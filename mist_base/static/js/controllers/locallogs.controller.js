(function () {
    'use strict';
 
    angular
        .module('app')
        .controller('Locallogs.IndexController', Controller, 'FileSaver', 'Blob');

    function Controller($scope, LocalLogsService, FileSaver, Blob) {
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
                if ($scope.id_to_path_map[_id].substr($scope.id_to_path_map[_id].length - 4) == '.log') {
                    LocalLogsService._get_local_log($scope.id_to_path_map[_id])
                        .then(
                            function (results) {
                                $scope.log_content = results.log_content.content;
                            }
                            , function (err) {
                                $scope.status = 'Error loading data: ' + err.message;
                            }
                        );
                }
                else {
                    LocalLogsService._get_archived_log($scope.id_to_path_map[_id])
                        .then(
                            function (data) {
                                var my_file = new Blob([data], {type: 'application/gzip'});
                                FileSaver.saveAs(my_file, $scope.id_to_path_map[_id]);
                            }
                            , function (err) {
                                $scope.status = 'Error loading data: ' + err.message;
                            }
                        );
                }
            }
        }
    }
})();
