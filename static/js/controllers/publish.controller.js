(function () {
    'use strict';
 
    angular
        .module('app')
        .controller('Publish.IndexController', Controller);

    function Controller($state, $scope, PublishSchedService, PublishJobsService, RepoPublishTimesService, PublishSitesService) {
        var vm = this;
        $scope._task = '';
        var obj_tasks = [];
        obj_tasks['publish.list'] = 'List Available Publications';
        obj_tasks['publish.on_demand'] = 'Publish On Demand';
        obj_tasks['publish.schedule'] = 'Schedule A Job';
        $scope.publish_sched_list = {};
        $scope.repo_publish_times_list = {};
        $scope.publish_jobs_list = {};
        vm.publish_sites_list = {};


        initController();

        function initController() {
            vm.loading = 0
            load_repo_publish_times();

            $scope._task = obj_tasks[$state.current.name];
            if ($state.current.name == 'publish.list') {
                load_publish_sites();
            }
            if ($state.current.name == 'publish.on_demand') {
                load_publish_sites();
            }
            if ($state.current.name == 'publish.schedule') {
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

        function load_publish_sites() {
            vm.loading += 1;
            PublishSitesService
                ._get_publishsites()
                .then(
                    function(results) {
                        vm.publish_sites_list = results.publish_sites_list;
                        vm.publish_sites_list.unshift({'id':0,'location':'localhost','name':'localhost'});
                        vm.selected_site = vm.publish_sites_list[0];
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
