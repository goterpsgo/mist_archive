(function () {
    'use strict';
 
    angular
        .module('app')
        .controller('Publish.IndexController', Controller);

    function Controller($scope, PublishSchedService, RepoPublishTimesService) {
        var vm = this;

        initController();

        function initController() {
            vm.loading = 0
        }

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
    }
})();
