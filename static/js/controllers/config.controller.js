(function () {
    'use strict';
 
    angular
        .module('app')
        .controller('Config.IndexController', Controller);

    function Controller($scope, $state, SecurityCentersService, BannerTextService, $timeout, Upload) {
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
        $scope.banner_text = {};

        initController();

        function initController() {
            $scope._task = obj_tasks[$state.current.name];
            if ($state.current.name == 'config.manage_security_centers') {
                load_sc_data();
            }
            if ($state.current.name == 'config.set_banner_text') {
                load_banner_text();
            }
        }
        
        $scope.select_task = function(_task) {
            $scope._task = _task;
        };

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
        }

        function load_banner_text() {
            BannerTextService
                ._get_bannertext()
                .then(
                      function(banner_text) {
                          $scope.banner_text['banner_text'] = banner_text.banner_text;

                      }
                    , function(err) {
                        $scope.status = 'Error loading data: ' + err.message;
                      }
                );
        }

        $scope.submit_sc_insert = function() {
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

        $scope.submit_banner_text= function() {
            console.log('[96] Got here insert');
            console.log($scope.banner_text);

            BannerTextService._delete_bannertext()
                .then(function() {
                    return BannerTextService._insert_bannertext($scope.banner_text)
                        .then(function(result) {
                            $scope.banner_text['status'] = result.data.response.message;
                            $scope.banner_text['status_class'] = result.data.response.class;
                            console.log('[105] Got here');
                        })
                        .then(function() {
                            load_banner_text();
                        })
                        .then(function() {
                            // clear status message after five seconds
                            $timeout(function() {
                                $scope.banner_text['status'] = '';
                                $scope.banner_text['status_class'] = '';
                            }, 5000);
                        }
                    );
                }
            );
        };

        $scope.submit_sc_update = function(index) {
            var _id = $scope.sc_list[index]['id'];

            SecurityCentersService._update_sc(_id, $scope.sc_list[index])
                .then(function(result) {
                    // display a status message to user
                    $scope.sc_list[index]['status'] = result.message;
                    $scope.sc_list[index]['status_class'] = result.class;
                })
                .then(function() {
                    // clear status message after five seconds
                    $timeout(function() {
                        $scope.sc_list[index]['status'] = '';
                        $scope.sc_list[index]['status_class'] = '';
                    }, 5000).then(function() {
                        load_sc_data();
                    });
                });

        };

        $scope.delete_sc = function(_id) {
            SecurityCentersService._delete_sc(_id)
                .then(
                      function() {
                        $scope.status = 'success';
                      }
                    , function(err) {
                        $scope.status = 'Error deleting data: ' + err.message;
                      }
                )
                .then(function() {
                        load_sc_data();
                });
        };
    }
})();
