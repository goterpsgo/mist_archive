(function () {
    'use strict';
 
    angular
        .module('app')
        .controller('Config.IndexController', Controller);

    function Controller($scope, $state, SecurityCentersService) {
        var vm = this;
        $scope._task = '';
        var obj_tasks = [];
        obj_tasks['config.global_parameters'] = 'Global Parameters';
        obj_tasks['config.set_banner_text'] = 'Set Banner Text';
        obj_tasks['config.set_classification_level'] = 'Set Classification Level';
        obj_tasks['config.manage_security_centers'] = 'Manage Security Centers';
        obj_tasks['config.manage_publishing_sites'] = 'Manage Publishing Sites';
        obj_tasks['config.remove_tag_definitions'] = 'Remove Tag Definitions';
        $scope.sc_list = []

        initController();

        function initController() {
            $scope._task = obj_tasks[$state.current.name];
            load_sc_data();
        }
        
        $scope.select_task = function(_task) {
            $scope._task = _task;
        }

        function load_sc_data() {
            SecurityCentersService
                ._get_scs()
                .then(
                      function(security_centers) {
                          $scope.sc_list = security_centers.sc_list;
                      }
                    , function(err) {
                        $scope.status = 'Error loading data: ' + err.message;
                      }
                );
        };
    }
})();
