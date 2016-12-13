(function () {
    'use strict';
 
    angular
        .module('app')
        .controller('Config.IndexController', Controller);

    function Controller($scope, $state) {
        var vm = this;
        $scope._task = '';
        var obj_tasks = [];
        obj_tasks['config.global_parameters'] = 'Global Parameters';
        obj_tasks['config.set_banner_text'] = 'Set Banner Text';
        obj_tasks['config.set_classification_level'] = 'Set Classification Level';
        obj_tasks['config.manage_security_centers'] = 'Manage Security Centers';
        obj_tasks['config.manage_publishing_sites'] = 'Manage Publishing Sites';
        obj_tasks['config.remove_tag_definitions'] = 'Remove Tag Definitions';

        initController();

        function initController() {
            $scope._task = obj_tasks[$state.current.name];
        }
        
        $scope.select_task = function(_task) {
            $scope._task = _task;
        }
    }
})();
