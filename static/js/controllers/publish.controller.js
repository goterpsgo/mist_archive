(function () {
    'use strict';
 
    angular
        .module('app')
        .controller('Publish.IndexController', Controller);

    function Controller($scope, PublishSchedService, PublishJobsService, RepoPublishTimesService) {
        var vm = this;
        $scope._task = '';
        var obj_tasks = [];
        obj_tasks['publish.list'] = 'Global Parameters';
        obj_tasks['publish.on_demand'] = 'Set Banner Text';
        obj_tasks['publish.schedule'] = 'Click Below to Set Classification Level';
        $scope.publish_sched_list = {};
        $scope.repo_publish_times_list = {};
        $scope.publish_jobs_list = {};

        initController();

        function initController() {
            vm.loading = 0
            load_repo_publish_times();

            $scope._task = obj_tasks[$state.current.name];
            if ($state.current.name == 'publish.list') {

            }
            if ($state.current.name == 'publish.manage_security_centers') {
                load_sc_data();
            }
            if ($state.current.name == 'publish.publish.schedule') {
                load_publish_sched();
            }
        }

        $scope.select_task = function(_task) {
            $scope._task = _task;
        };

        function load_publish_sched() {
            vm.loading += 1;
            PublishSchedService
                ._get_publishsched()
                .then(
                    function(results) {
                        $scope.publish_sched_list = results.publish_sched_list;
                        vm.loading = false;
                      }
                    , function(err) {
                        $scope.status = 'Error loading data: ' + err.message;
                        vm.loading -= 1;
                      }
                );
        }

        function load_repo_publish_times() {
            vm.loading += 1;
            RepoPublishTimesService
                ._get_repopublishtimes()
                .then(
                    function(results) {
                        $scope.repo_publish_times_list = results.repo_publish_times_list;
                        vm.loading = false;
                      }
                    , function(err) {
                        $scope.status = 'Error loading data: ' + err.message;
                        vm.loading -= 1;
                      }
                );
        }

        function load_publish_jobs() {
            vm.loading += 1;
            PublishJobsService
                ._get_publishjobs()
                .then(
                    function(results) {
                        $scope.publish_jobs_list = results.publish_jobs_list;
                        vm.loading = false;
                      }
                    , function(err) {
                        $scope.status = 'Error loading data: ' + err.message;
                        vm.loading -= 1;
                      }
                );
        }
    }
})();
