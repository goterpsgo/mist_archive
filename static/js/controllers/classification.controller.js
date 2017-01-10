(function () {
    'use strict';
 
    angular
        .module('app')
        .controller('Classification.IndexController', Controller);

    function Controller($scope, $rootScope, $state, ClassificationService, $timeout, Upload) {
        var vm = this;
        $rootScope.classification = {};

        initController();

        function initController() {
            load_classification();
        }

        function load_classification() {
            ClassificationService
                ._get_classification()
                .then(
                      function(classification) {
                          if (classification.classifications_list[0].display == 'None') {
                              classification.classifications_list[0].display = '';
                          }
                          $rootScope.classification = classification.classifications_list[0];
                      }
                    , function(err) {
                        $scope.status = 'Error loading data: ' + err.message;
                      }
                );
        }
    }
})();
