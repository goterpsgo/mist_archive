(function () {
    'use strict';
 
    angular
        .module('app')
        .controller('Config.IndexController', Controller);

    function Controller($scope, $state, SecurityCentersService, $timeout) {
        var vm = this;
        $scope._task = '';
        var obj_tasks = [];
        obj_tasks['config.global_parameters'] = 'Global Parameters';
        obj_tasks['config.set_banner_text'] = 'Set Banner Text';
        obj_tasks['config.set_classification_level'] = 'Set Classification Level';
        obj_tasks['config.manage_security_centers'] = 'Manage Security Centers';
        obj_tasks['config.manage_publishing_sites'] = 'Manage Publishing Sites';
        obj_tasks['config.remove_tag_definitions'] = 'Remove Tag Definitions';
        $scope.sc_list = []; // used for binding forms for updating existing SC entries
        // use for binding form for inserting new SC entry
        $scope.form_data = {
              'version': 5    // check version 5 as default version for new entries
        };

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

        $scope.submit_sc_insert = function() {
            console.log('[49] Got here insert');
            console.log($scope.form_data);

            return SecurityCentersService._create_sc($scope.form_data)
                .then(function(result) {
                    // $scope.response_message = result.response.message;
                    // $scope.result = result.response.result;
                    // $scope.class = result.response.class;
            });
        };

        $scope.submit_sc_update = function(index) {
            console.log('[54] Got here update');
            console.log($scope.sc_list[index]);
        };

        $scope.delete_sc = function(index) {
            console.log('[59] Got here delete');
            console.log($scope.sc_list[index]);
            var _id = $scope.sc_list[index]['id'];
            SecurityCentersService._delete_sc(_id)
                .then(
                      function() {
                        $scope.status = 'success';
                      }
                    , function(err) {
                        $scope.status = 'Error deleting data: ' + err.message;
                      }
                );

            // Delay get_users() by 1ms to not overwhelm the database (unless there's a better solution - JWT 6 Dec 2016)
            $timeout(function() {
                load_sc_data();
            }, 1);
        };
    }
})();
