(function () {
    'use strict';
 
    angular
        .module('app')
        .controller('Repostag.IndexController', Controller);

    function Controller($q, $scope, $timeout, $localStorage, MistUsersService, TagDefinitionsService, CategorizedTagsService, TaggedReposService, ReposService, $mdDialog) {
        var vm = this;
        $scope.tag_definitions = {};
        $scope.assigned_tag_definition = {"value": 23};
        $scope.categorized_tags = {};
        $scope.treeData = {"value": "Loading..."};
        $scope.tags_tree = null;
        $scope.profile = {};
        $scope.cardinality = {};
        $scope.assign_repos = [];
        $scope.form_fields = {'tagMode': 'Repo', 'cardinality': 1};
        $scope.rollup_track_by_repo = {};
        $scope.status = {};

        initController();

        function initController() {
            var deferred = $q.defer();
            var promise = deferred.promise;

            promise
                .then(function(val) {
                    get_repos();
                })
                .then(function(val) {
                    get_this_user();
                })
                .then(function(val) {
                    load_tag_definitions();
                })
                .then(function(val) {
                    load_categorized_tags(26);
                })
            ;

            deferred.resolve();
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
            // $scope.assigned_tag_definition = $scope.tag_definitions[5];
        }

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

        function get_this_user() {
            var username = $localStorage.currentUser.username;
            $scope.rollup_track_by_repo = {};
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

                                  if (($scope.rollup_track_by_repo[key] == undefined) && (repo.tags.length > 0)) {
                                      $scope.rollup_track_by_repo[key] = [];
                                  }

                                  if (repo.tags.length > 0) {
                                      for (var _cnt_rollup = 0; _cnt_rollup < repo.tags.length; _cnt_rollup++) {
                                          $scope.rollup_track_by_repo[key].push(repo.tags[_cnt_rollup].rollup);
                                      }
                                  }
                              })
                          }
                      }
                    , function(err) {
                        $scope.status = 'Error loading data: ' + err.message;
                      }
                );
        }

        $scope.load_tags = function() {
            load_categorized_tags($scope.assigned_tag_definition.id);
        }

        $scope.delete_tagging = function(_tagged_repos_id) {
            TaggedReposService
                ._delete_taggedrepos(_tagged_repos_id)
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
                        get_this_user();    // reload list of user-assigned repos and tags
                        get_repos();
                        // clear status message after five seconds
                        $timeout(function() {
                            $scope.status = '';
                        }, 5000);
                    }
                );
        }

        function auto_tag() {
            $scope.form_fields['tree_nodes'] = [];
            if ($$("tags_tree").getSelectedId() instanceof Array) {
                $scope.form_fields['tree_nodes'] = $$("tags_tree").getSelectedId();
            }
            else {
                $scope.form_fields['tree_nodes'].push($$("tags_tree").getSelectedId());
            }

            $scope.form_fields['selected_repos'] = [];
            for (var _cnt = 0; _cnt < $scope.profile.assign_repos.length; _cnt++) {
                if ($scope.profile.assign_repos[_cnt].is_checked == true) {
                    $scope.form_fields['selected_repos'].push(
                        {'sc_id': $scope.profile.assign_repos[_cnt].sc_id, 'repo_id': $scope.profile.assign_repos[_cnt].repo_id}
                    );
                }
            }

            if (($scope.form_fields['tree_nodes'].length == 0) || ($scope.form_fields['tree_nodes'][0] == '')) {
                check_values_warning();
                return;
            }

            $scope.form_fields['username'] = $scope.profile.username;
            $scope.form_fields['cardinality'] = $scope.cardinality[$scope.assigned_tag_definition.id];

            TaggedReposService
                ._insert_taggedrepos($scope.form_fields)
                .then(
                      function(result) {
                        $scope.status = result.data.response;
                      }
                    , function(err) {
                        $scope.status = 'Error loading data: ' + err.message;
                      }
                )
                .then(
                    function() {
                        get_this_user();    // reload list of user-assigned repos and tags
                        get_repos();
                        // clear status message after five seconds
                        $timeout(function() {
                            $scope.status = '';
                        }, 5000);
                    }
                );
        }

        $scope.submit_auto_tag = function() {
            if ($scope.assigned_tag_definition.cardinality > 1) {
                auto_tag();
            }
            else {
                // note all checked off repos and save them to _checked_repos
                var _checked_repos = [];
                for (var _cnt = 0; _cnt < $scope.profile.assign_repos.length; _cnt++) {
                    if ($scope.profile.assign_repos[_cnt].is_checked == true) {
                        var _repo = $scope.profile.assign_repos[_cnt];
                        _checked_repos.push(_repo.server_name+','+_repo.repo_name+','+_repo.repo_id+','+_repo.sc_id);
                    }
                }

                if (_checked_repos.length == 0) {
                    check_values_warning();
                    return;
                }

                // if one or more checked repo is in list of repo with tags then mark found_key as true
                var found_key = false;
                for (var _cnt = 0; _cnt < _checked_repos.length; _cnt++) {
                    var _checked_repo = _checked_repos[_cnt];
                    if ($scope.rollup_track_by_repo[_checked_repo] != undefined) {
                        found_key = true;
                        break;
                    }
                }

                // print user confirm modal window
                if (found_key) {
                    var confirm = $mdDialog.confirm()
                        .title('Overwrite current tags?')
                        .textContent('You have selected a tag category with a cardinality of 1. You have selected one more more repos already associated wtih a tag of that category. Overwrite entry?')
                        .ok('Replace Current Tag')
                        .cancel('Cancel Operation');

                    $mdDialog.show(confirm).then(function() {
                        auto_tag();
                    }, function() {
                        console.log('Cancel Operation');
                    });
                }
                else {
                    auto_tag();
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

        $scope.refresh_data = function() {
            get_repos();
        };
    }
})();
