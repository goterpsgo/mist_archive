(function () {
    'use strict';
 
    angular
        .module('app')
        .controller('Publish.IndexController', Controller);

    function Controller($state, $scope, $timeout, $localStorage, PublishSchedService, PublishJobsService, RepoPublishTimesService, PublishSitesService, MistParamsService) {
        var vm = this;
        $scope._task = '';
        var obj_tasks = [];
        obj_tasks['publish.list'] = 'List Available Publications';
        obj_tasks['publish.on_demand'] = 'Publish On Demand';
        obj_tasks['publish.schedule'] = 'Schedule A Job';
        $scope.publish_sched_list = {};
        $scope.repo_publish_times = {};
        $scope.publish_jobs_list = {};
        vm.publish_sites_list = {};
        $scope.status = '';
        $scope.this_date = new Date();

        $scope.scan_options = {"cve": false, "benchmark": false, "iavm": false, "plugin": false, "all_scan": false};
        $scope.asset_options = {"assets": false, "opattr": false, "all_asset": false};

        $scope.grid_options = {
            columnDefs: $scope.column_names,
            // enableSorting: true,
            'data': []
        };


        initController();

        function initController() {
            vm.loading = 0
            load_repo_publish_times();

            $scope._task = obj_tasks[$state.current.name];
            if ($state.current.name == 'publish.list') {
                load_publish_jobs();
                load_mist_params();
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
                        $scope.repo_publish_times = results.repo_publish_times;
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

                        // [kept for reference] [ES5] array forEach loop
                        // $scope.publish_jobs_list.forEach(function(_row, _index, _ref) {
                        //     if (_row.status == 'Completed') {
                        //         _ref[_index].filename = '<a href="#">' + _row.filename + '</a>';
                        //     }
                        // });

                        // [kept for reference] Displaying links in ui-grid cell
                        // $scope.column_names = [
                        //     {
                        //       "name": "Filename"
                        //       , "displayName": "Filename"
                        //       , "field": "filename"
                        //       , "width": 350
                        //       , cellTemplate: '<div><a href="#">{{row.entity.filename}}</a></div>'
                        //     },
                        //     {
                        //       "name": "PublishDate"
                        //       , "displayName": "Publish Date"
                        //       , "field": "finishTime"
                        //       , "width": 150
                        //       , "sort": {"direction": "desc", "priority": 0}
                        //     },
                        //     {
                        //       "name": "Status"
                        //       , "displayName": "Status"
                        //       , "field": "status"
                        //     },
                        //     {
                        //       "name": "PublishedBy"
                        //       , "displayName": "Published By"
                        //       , "field": "userName"
                        //     }
                        // ];
                        // $scope.grid_options = {
                        //     columnDefs: $scope.column_names
                        // };
                        // $scope.grid_options.data = results.publish_jobs_list;
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
                        vm.selected_site = vm.publish_sites_list[0];    // setting default selection in here may be bad practice; didn't work when tried in init() - JWT 2 Mar 2017
                        vm.loading = false;
                      }
                    , function(err) {
                        $scope.status = 'Error loading data: ' + err.message;
                        vm.loading -= 1;
                      }
                );
        }

        $scope.publish_on_demand = function() {
            vm.user = ' --user ' + $localStorage.user.id;
            vm.site = ' --site "' + vm.selected_site + '"';
            vm.options = vm.user + vm.site;

            for (var _node in $scope.scan_options) {
                if ($scope.scan_options[_node]) {
                    vm.options += ' --' + _node;
                }
            }

            for (var _node in $scope.asset_options) {
                if ($scope.asset_options[_node]) {
                    vm.options += ' --' + _node;
                }
            }

            var form_data = {'job_type': 'on_demand', 'options': vm.options};
            return PublishJobsService
                ._insert_publishjobs(form_data)
                .then(function(result) {
                    $scope.status = 'Executed publish on demand.';
                    $scope.status_class = 'alert alert-success';
                })
                .then(function() {
                    // clear status message after five seconds
                    $timeout(function() {
                        $scope.status = '';
                        $scope.status_class = '';
                    }, 5000);
                });


            // return SecurityCentersService._insert_sc($scope.form_data).then()
            //     .then(function(result) {
            //         $scope.form_data['status'] = result.message;
            //         $scope.form_data['status_class'] = result.class;
            //         $scope.form_data['serverName'] = '';
            //         $scope.form_data['fqdn_IP'] = '';
            //         $scope.form_data['username'] = '';
            //         $scope.form_data['pw'] = '';
            //         $scope.form_data['certificateFile'] = '';
            //         $scope.form_data['keyFile'] = '';
            //         $scope.form_data['version'] = 5;
            //     })
            //     .then(function() {
            //         load_sc_data();
            //     })
            //     .then(function() {
            //         // clear status message after five seconds
            //         $timeout(function() {
            //             $scope.form_data['status'] = '';
            //             $scope.form_data['status_class'] = '';
            //         }, 5000);
            //     });

        };

        function load_mist_params() {
            MistParamsService
                ._get_mist_params()
                .then(
                    function(results) {
                        var _mist_params = results.mist_params_list[0];
                        // $scope._mist_params = _mist_params;
                        $scope.assign_chunk_size = _mist_params.chunkSize;
                        $scope.assign_log_rollover = _mist_params.logsRollOverPeriod;
                        $scope.assign_pub_rollover = _mist_params.pubsRollOverPeriod;
                        $scope.assign_assets_refresh = _mist_params.scPullFreq;
                      }
                    , function(err) {
                          $scope.status = 'Error loading data: ' + err.message;
                      }
                );
        }
    }
})();
