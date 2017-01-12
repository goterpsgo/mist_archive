(function () {
    'use strict';
 
    angular
        .module('app')
        .controller('Config.IndexController', Controller);

    function Controller($scope, $rootScope, $state, SecurityCentersService, BannerTextService, ClassificationService, MistParamsService, TagDefinitionsService, PublishSitesService, $timeout, Upload) {
        var vm = this;
        $scope._task = '';
        var obj_tasks = [];
        obj_tasks['config.global_parameters'] = 'Global Parameters';
        obj_tasks['config.set_banner_text'] = 'Set Banner Text';
        obj_tasks['config.set_classification_level'] = 'Click Below to Set Classification Level';
        obj_tasks['config.manage_security_centers'] = 'Manage Security Centers';
        obj_tasks['config.manage_publish_sites'] = 'Manage Publishing Sites';
        obj_tasks['config.manage_tag_definitions'] = 'Manage Tag Definitions';
        $scope.sc_list = []; // used for binding forms for updating existing SC entries
        // use for binding form for inserting new SC entry
        $scope.form_data = {
              'version': 5    // check version 5 as default version for new entries
        };
        $scope._classifications = [];
        $scope.classification = {};
        $scope.banner_text = {};
        $scope._mist_params = {};
        $scope._mist_params_assigned = {};
        $scope.tag_definitions = [];
        $scope.publish_sites_list = [];
        $scope.new_td = {
              'cardinality': 1
            , 'required': 'N'
        };
        $scope.new_ps = {};

        initController();

        function initController() {
            $scope._task = obj_tasks[$state.current.name];
            if ($state.current.name == 'config.global_parameters') {
                load_mist_params();
            }
            if ($state.current.name == 'config.manage_security_centers') {
                load_sc_data();
            }
            if ($state.current.name == 'config.set_banner_text') {
                load_banner_text();
            }
            if ($state.current.name == 'config.set_classification_level') {
                load_classifications();
            }
            if ($state.current.name == 'config.manage_publish_sites') {
                load_publish_sites();
            }
            if ($state.current.name == 'config.manage_tag_definitions') {
                load_tag_definitions();
            }
        }
        
        $scope.select_task = function(_task) {
            $scope._task = _task;
        };

        function load_sc_data() {
            vm.loading = true;
            SecurityCentersService
                ._get_scs()
                .then(
                      function(security_centers) {
                        $scope.sc_list = security_centers.sc_list;
                        vm.loading = false;
                      }
                    , function(err) {
                        $scope.status = 'Error loading data: ' + err.message;
                        vm.loading = false;
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

        function load_classification() {
            ClassificationService
                ._get_classification()
                .then(
                      function(classification) {
                          $scope.classification = classification.classifications_list[0];
                      }
                    , function(err) {
                        $scope.status = 'Error loading data: ' + err.message;
                      }
                );
        }

        function load_classifications() {
            ClassificationService
                ._get_classifications()
                .then(
                      function(classifications) {
                          $scope._classifications = classifications.classifications_list;
                      }
                    , function(err) {
                          $scope.status = 'Error loading data: ' + err.message;
                      }
                );
        }

        function refresh_classifications() {
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

        $scope.update_classification = function(id) {
            ClassificationService
                ._update_classification(id)
                .then(
                      function(classifications) {
                          refresh_classifications();
                      }
                    , function(err) {
                          $scope.status = 'Error loading data: ' + err.message;
                      }
                );
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

        function update_mist_params(_field_name, _value) {
            MistParamsService
                ._update_mist_param(_field_name, _value)
                .then(
                      function(results) {
                          // no results shown back to user unless we figure out otherwise
                      }
                    , function(err) {
                          $scope.status = 'Error loading data: ' + err.message;
                      }
                );
        }

        $scope.update_param_value = function (_field_name) {
            switch(_field_name) {
                case 'assign_chunk_size':
                    update_mist_params('chunkSize', $scope.assign_chunk_size);
                    break;
                case 'assign_log_rollover':
                    update_mist_params('logsRollOverPeriod', $scope.assign_log_rollover);
                    break;
                case 'assign_pub_rollover':
                    update_mist_params('pubsRollOverPeriod', $scope.assign_pub_rollover);
                    break;
                case 'assign_assets_refresh':
                    update_mist_params('scPullFreq', $scope.assign_assets_refresh);
                    break;
            }
        };

        function load_tag_definitions() {
            vm.loading = true;
            TagDefinitionsService
                ._get_tagdefinitions()
                .then(
                    function(results) {
                        $scope.tag_definitions = results.tag_definitions;
                        vm.loading = false;
                      }
                    , function(err) {
                        $scope.status = 'Error loading data: ' + err.message;
                        vm.loading = false;
                      }
                );
        }

        $scope.add_new_td = function() {
            return TagDefinitionsService._insert_tagdefinition($scope.new_td)
                .then(function() {
                    load_tag_definitions();
                    $scope.new_td = {
                          'cardinality': 1
                        , 'required': 'N'
                    };
                });
        };

        $scope.update_td_param_value = function(_id, _name, _value) {
            var upd_form = '{"' + _name + '": "' + _value + '"}';
            TagDefinitionsService
                ._update_td_param(_id, upd_form)
                .then(
                      function(users) {
                          load_tag_definitions();
                      }
                    , function(err) {
                        $scope.status = 'Error loading data: ' + err.message;
                      }
                );
        }

        $scope.delete_td = function(_id) {
            TagDefinitionsService
                ._delete_tagdefinition(_id)
                .then(
                      function(users) {
                          load_tag_definitions();
                      }
                    , function(err) {
                        $scope.status = 'Error loading data: ' + err.message;
                      }
                );
        }


        function load_publish_sites() {
            vm.loading = true;
            PublishSitesService
                ._get_publishsites()
                .then(
                    function(results) {
                        $scope.publish_sites_list = results.publish_sites_list;
                        vm.loading = false;
                      }
                    , function(err) {
                        $scope.status = 'Error loading data: ' + err.message;
                        vm.loading = false;
                      }
                );
        }

        $scope.add_new_ps = function() {
            return PublishSitesService
                ._insert_publishsite($scope.new_ps)
                .then(function() {
                    load_publish_sites();
                    $scope.new_ps = {};
                });
        };

        $scope.update_ps_param_value = function(_id, _name, _value) {
            var upd_form = '{"' + _name + '": "' + _value + '"}';
            PublishSitesService
                ._update_ps_param(_id, upd_form)
                .then(
                      function(users) {
                          load_publish_sites();
                      }
                    , function(err) {
                        $scope.status = 'Error loading data: ' + err.message;
                      }
                );
        }

        $scope.delete_ps = function(_id) {
            PublishSitesService
                ._delete_publishsite(_id)
                .then(
                      function(users) {
                          load_publish_sites();
                      }
                    , function(err) {
                        $scope.status = 'Error loading data: ' + err.message;
                      }
                );
        }
    }
})();
