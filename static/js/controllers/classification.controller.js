(function () {
    'use strict';
 
    angular
        .module('app')
        .controller('Classification.IndexController', Controller);

    function Controller($scope, $state, ClassificationService, $timeout, Upload) {
        var vm = this;
        var classes = [];
        classes['None'] = '';
        classes['Unclassified'] = 'bg-unclassified';
        classes['Confidential'] = 'bg-confidential';
        classes['Secret'] = 'bg-secret';
        classes['Top Secret'] = 'bg-top-secret';
        classes['Top Secret - No Foreign'] = 'bg-tssci';
        $scope.classification = {};

        initController();

        function initController() {
            load_classification();
        }
        
        $scope.select_task = function(_task) {
            $scope._task = _task;
        };

        function load_classification() {
            ClassificationService
                ._load_classification()
                .then(
                      function(classification) {
                          $scope.classification['classification'] = classification.classifications_list[0];
                          $scope.classification['class'] = classes[classification.classifications_list[0]['level']];
                          console.log('[37] Got here: ' + classification.classifications_list[0]['level']);
                      }
                    , function(err) {
                        $scope.status = 'Error loading data: ' + err.message;
                      }
                );
        }

        $scope.update_classification_text = function() {
            console.log($scope.form_data);

            return SecurityCentersService._insert_sc($scope.form_data).then()
                .then(function(result) {
                    $scope.form_data['status'] = result.message;
                    $scope.form_data['status_class'] = result.class;
                    $scope.form_data['serverName'] = '';
                    $scope.form_data['fqdn_IP'] = '';
                    $scope.form_data['username'] = '';
                    $scope.form_data['pw'] = '';
                    $scope.form_data['certificateFile'] = '';
                    $scope.form_data['keyFile'] = '';
                    $scope.form_data['version'] = 5;
                })
                .then(function() {
                    load_sc_data();
                })
                .then(function() {
                    // clear status message after five seconds
                    $timeout(function() {
                        $scope.form_data['status'] = '';
                        $scope.form_data['status_class'] = '';
                    }, 5000);
                });
        };
    }
})();
