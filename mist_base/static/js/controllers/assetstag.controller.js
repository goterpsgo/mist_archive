(function () {
    'use strict';
 
    angular
        .module('app')
        .controller('Assetstag.IndexController', Controller);

    function Controller($q, $scope, $timeout, $localStorage, MistUsersService, TagDefinitionsService, CategorizedTagsService, TaggedReposService, ReposService, AssetsService, $mdDialog) {
        var vm = this;
        $scope.tag_definitions = {};
        $scope.assigned_tag_definition = {"value": 23};
        $scope.categorized_tags = {};
        $scope.treeData = {"value": "Loading..."};
        $scope.tags_tree = null;
        $scope.profile = {
            "assign_repos": [{"server_name": "label", "repo_id": "value"}]
        };
        $scope.cardinality = {};
        $scope.form_fields = {'tagMode': 'Repo', 'cardinality': 1};
        $scope.search_form = {
              "search_description": "Search Category Description"
            , "category_dropdown": [
                  {"value": "assets_ip", "text": "IP", "desc": "IP range could be specified in CIDR format (e.g. 10.11.1.0/24) or Dot format 10.11.1.0-10.11.1.64"}
                , {"value": "assets_dnsName", "text": "DNS Name", "desc": "Assets (in all assigned repositories) having the specified field containing the search string will be returned."}
                , {"value": "assets_osCPE", "text": "OS", "desc": "Assets (in all assigned repositories) having the specified field containing the search string will be returned."}
                , {"value": "assets_macAddress", "text": "MAC Address", "desc": "Assets (in all assigned repositories) having the specified field containing the search string will be returned."}
                , {"value": "assets_netbiosName", "text": "NetBIOS Name", "desc": "Assets (in all assigned repositories) having the specified field containing the search string will be returned."}
                , {"value": "assets_biosGUID", "text": "BIOS GUID", "desc": "Assets (in all assigned repositories) having the specified field containing the search string will be returned."}
                , {"value": "assets_mcafeeGUID", "text": "McAfee GUID", "desc": "Assets (in all assigned repositories) having the specified field containing the search string will be returned."}
                , {"value": "repos", "text": "Repository", "desc": "Assets (in all assigned repositories) of which the names containing the search string will be returned."}
              ]
        };
        $scope.search_form.category = {};
        $scope.rollup_track_by_asset = {};

        $scope.assets_list = [];
        $scope.status = {};

        initController();

        function initController() {
            var deferred = $q.defer();
            var promise = deferred.promise;

            promise
                .then(function(val) {
                    get_this_user();
                    console.log($scope.assets_list);
                })
                .then(function(val) {
                    get_repos();
                })
                .then(function(val) {
                    load_tag_definitions();
                })
                .then(function(val) {
                    load_categorized_tags(26);
                })
            ;

            deferred.resolve();
            $scope.search_form.category = $scope.search_form.category_dropdown[0];
        }

        function load_tag_definitions() {
            vm.loading = true;
            TagDefinitionsService
                ._get_tagdefinitions()
                .then(
                    function(results) {
                        $scope.tag_definitions = results.tag_definitions;
                        for (var _cnt = 0; _cnt < $scope.tag_definitions.length; _cnt++) {
                            $scope.cardinality[$scope.tag_definitions[_cnt]['id']] = $scope.tag_definitions[_cnt]['cardinality'];
                        }
                        $scope.assigned_tag_definition = $scope.tag_definitions[5];
                        vm.loading = false;
                      }
                    , function(err) {
                        $scope.status = 'Error loading data: ' + err.message;
                        vm.loading = false;
                      }
                );
        }

        // loading tags into tag tree in left window
        function load_categorized_tags(_id) {
            vm.loading = true;
            $scope.treeData = {"value": "Loading..."};
            CategorizedTagsService
                ._get_categorizedtags(_id)
                .then(
                      function(results) {
                        $scope.treeData = results.treeData;
                        // single or multiple tree node select based on cardinality
                        $$("tags_tree").config.select = ($scope.cardinality[_id] == 1) ? 'select' : 'multiselect';
                        vm.loading = false;
                      }
                    , function(err) {
                        $scope.status = 'Error loading data: ' + err.message;
                        vm.loading = false;
                      }
                )
            ;
        }

        // add user-readable names to assigned repos list
        function load_user_assigned_repos() {
            // Add additional information from assign_repos to profile.assign_repos
            for (var _cnt = 0; _cnt < $scope.profile.assign_repos.length; _cnt++) {
                for (var _cnt2 = 0; _cnt2 < $scope.assign_repos.length; _cnt2++) {
                    if (($scope.profile.assign_repos[_cnt]['repo_id'] == $scope.assign_repos[_cnt2]['repo_id'])
                        && ($scope.profile.assign_repos[_cnt]['sc_id'] == $scope.assign_repos[_cnt2]['sc_id'])) {
                        $scope.profile.assign_repos[_cnt]['repo_name'] = $scope.assign_repos[_cnt2]['repo_name'];
                        $scope.profile.assign_repos[_cnt]['server_name'] = $scope.assign_repos[_cnt2]['server_name'];
                        break;
                    }
                }
            }
        }

        function get_repos() {
            ReposService._get_repos()
                .then(
                      function(repos) {
                          $scope.assign_repos = repos.repos_list;
                      }
                    , function(err) {
                        $scope.status = 'Error loading data: ' + err.message;
                      }
                )
                .then(function() {
                    load_user_assigned_repos();
                });
        }

        function load_assets() {
            // Service will not trigger unless a repo is supplied or category and search string are supplied
            AssetsService
                ._get_assets($scope.search_form)
            .then(
                  function(result) {
                    $scope.assets_list = result.assets_list;
                    console.log($scope.assets_list);

                    for (var _cnt_assets = 0; _cnt_assets < $scope.assets_list.length; _cnt_assets++) {
                        var _asset = $scope.assets_list[_cnt_assets];
                        if (($scope.rollup_track_by_asset[_asset.assetID] == undefined) && (Object.keys(_asset.tags).length > 0)) {
                            $scope.rollup_track_by_asset[_asset.assetID] = []
                        }
                        if ((Object.keys(_asset.tags).length > 0)) {
                            angular.forEach(_asset.tags, function(tag, key) {
                                $scope.rollup_track_by_asset[_asset.assetID].push(_asset.tags[key].rollup);

                                // Remove duplicate values from $scope.rollup_track_by_asset[_asset.assetID]
                                // http://mikeheavers.com/tutorials/removing_duplicates_in_an_array_using_javascript/
                                $scope.rollup_track_by_asset[_asset.assetID] = $scope.rollup_track_by_asset[_asset.assetID].filter(function(elem, pos) {
                                    return $scope.rollup_track_by_asset[_asset.assetID].indexOf(elem) == pos;
                                });
                            })
                        }
                    }
                  }
                , function(err) {
                    $scope.status = 'Error loading data: ' + err.message;
                  }
            );
        }

        function get_this_user() {
            var username = $localStorage.currentUser.username;
            $scope.rollup_track_by_asset = {};
            MistUsersService._get_user(username)
                .then(
                      function(user) {
                          $scope.profile = user.users_list[0];

                          // if there are assigned repos for given user, add .repos[] entries to bound .assign_repos array for dropdown selections
                          if (Object.keys($scope.profile.repos).length > 0) {
                              $scope.profile.assign_repos = [];
                              angular.forEach($scope.profile.repos, function(repo, key) {
                                  repo.tags['is_checked'] = false;
                                  var selected_repo_entry = {'repo_id': repo.repoID, 'sc_id': repo.scID, 'is_checked': false, 'tags': repo.tags};
                                  $scope.profile.assign_repos.push(selected_repo_entry);
                              });
                              $scope.search_form.repo = $scope.profile.assign_repos[0];
                              load_assets();
                          }
                      }
                    , function(err) {
                        $scope.status = 'Error loading data: ' + err.message;
                      }
                );
        }

        $scope.load_tags = function() {
            load_categorized_tags($scope.assigned_tag_definition.id);
        };

        $scope.load_assets = function() {
            load_assets();
        };

        $scope.update_search = function() {
            // load_assets();
            $scope.search_form.search_description = $scope.search_form.category.desc;
        };

        // TODO: remove affected keys from $scope.rollup_track_by_asset
        $scope.delete_tagging = function(_id, _assetID, rollup) {
            console.log($scope.rollup_track_by_asset);
            for (var _cnt in $scope.rollup_track_by_asset[_assetID]) {
                var _this_rollup = $scope.rollup_track_by_asset[_assetID][_cnt]
                if (_this_rollup == rollup) {
                    $scope.rollup_track_by_asset[_assetID].splice(_cnt);
                }
            }
            console.log(_id);
            AssetsService
                ._delete_asset_tag(_id)
                .then(
                      function(result) {
                        $scope.status = result.response;
                      }
                    , function(err) {
                        $scope.status = 'Error loading data: ' + err.message;
                      }
                )
                .then(
                    function() {
                        load_assets();
                        // clear status message after five seconds
                        $timeout(function() {
                            $scope.status = '';
                        }, 5000);
                    }
                );
            console.log($scope.rollup_track_by_asset);
        };

        function manual_tag() {
            $scope.form_fields['tree_nodes'] = [];
            if ($$("tags_tree").getSelectedId() instanceof Array) {
                $scope.form_fields['tree_nodes'] = $$("tags_tree").getSelectedId();
            }
            else {
                $scope.form_fields['tree_nodes'].push($$("tags_tree").getSelectedId());
            }

            $scope.form_fields['selected_assets'] = [];
            for (var _cnt = 0; _cnt < $scope.assets_list.length; _cnt++) {
                if ($scope.assets_list[_cnt].is_checked == true) {
                    $scope.form_fields['selected_assets'].push(
                        {'assetID': $scope.assets_list[_cnt].assetID, 'ip': $scope.assets_list[_cnt].ip}
                    );
                }
            }

            if (($scope.form_fields['tree_nodes'].length == 0) || ($scope.form_fields['tree_nodes'][0] == '')) {
                check_values_warning();
                return;
            }

            $scope.form_fields['tagMode'] = 'Manual';
            $scope.form_fields['username'] = $scope.profile.username;
            $scope.form_fields['cardinality'] = $scope.cardinality[$scope.assigned_tag_definition.id];

            // console.log($$("tags_tree").getSelectedId());
            // console.log($$("tags_tree").getChecked());

            AssetsService
                ._insert_taggedassets($scope.form_fields)
                .then(
                      function(result) {
                        $scope.status = result.response;
                      }
                    , function(err) {
                        $scope.status = 'Error loading data: ' + err.message;
                      }
                )
                .then(
                    function() {
                        load_assets();
                        get_repos();
                        // clear status message after five seconds
                        $timeout(function() {
                            $scope.status = '';
                        }, 5000);
                    }
                );
        }

        $scope.submit_manual_tag = function() {
            if ($scope.assigned_tag_definition.cardinality > 1) {
                manual_tag();
            }
            else {
                // note all checked off assets and save them to _checked_assets
                console.log($scope.rollup_track_by_asset);
                var _checked_assets = [];
                var _checked_asset_ids = [];
                for (var _cnt = 0; _cnt < $scope.assets_list.length; _cnt++) {
                    if ($scope.assets_list[_cnt].is_checked == true) {
                        var _asset = $scope.assets_list[_cnt];
                        _checked_assets.push(_asset);
                        _checked_asset_ids.push(_asset.assetID);
                    }
                }

                if (_checked_assets.length == 0) {
                    check_values_warning();
                    return;
                }

                // if one or more checked repo is in list of repo with tags then mark found_key as true
                var found_key = false;
                for (var _cnt = 0; _cnt < _checked_assets.length; _cnt++) {
                    var _checked_asset_id = _checked_assets[_cnt].assetID;
                    // Need to track $scope.rollup_track_by_asset[_checked_asset_id].length
                    // since it still exists if the tag is deleted but the array length is now zero
                    if (($scope.rollup_track_by_asset[_checked_asset_id] != undefined) && ($scope.rollup_track_by_asset[_checked_asset_id].length != 0)) {
                        found_key = true;
                        break;
                    }
                }

                console.log($scope.rollup_track_by_asset);
                // print user confirm modal window
                if (found_key) {
                    var confirm = $mdDialog.confirm()
                        .title('Overwrite current tags?')
                        .textContent('You have selected a tag category with a cardinality of 1. You have selected one more more assets already associated wtih a tag of that category. Overwrite entry?')
                        .ok('Replace Current Tag')
                        .cancel('Cancel Operation');

                    $mdDialog.show(confirm).then(function() {
                        manual_tag();
                    }, function() {
                        console.log('Cancel Operation');
                    });
                }
                else {
                    manual_tag();
                }
            }
        };

        function check_values_warning() {
            $scope.status.result = 'Error:';
            $scope.status.message = 'Please make one or more selections from both panes and click Save.';
            $scope.status.class = 'alert alert-warning';

            // clear status message after five seconds
            $timeout(function () {
                $scope.status.result = '';
                $scope.status.message = '';
                $scope.status.class = '';
            }, 5000);
        }

        vm.check_all = function() {
            for (var _cnt in $scope.assets_list) {
                $scope.assets_list[_cnt].is_checked = vm.is_check_all;
            }
        };

        $scope.refresh_data = function() {
            get_repos();
        };
    }
})();
