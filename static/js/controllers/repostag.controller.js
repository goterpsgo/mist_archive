(function () {
    'use strict';
 
    angular
        .module('app')
        .controller('Repostag.IndexController', Controller);

    function Controller($scope, $timeout, $localStorage, MistUsersService, TagDefinitionsService, CategorizedTagsService, ReposService) {
        var vm = this;
        $scope.tag_definitions = {};
        $scope.assigned_tag_definition = {"value": 23};
        $scope.categorized_tags = {};
        $scope.treeData = {"value": "Loading..."};
        $scope.tags_tree = null;
        $scope.profile = {};
        $scope.cardinality = {};
        $scope.assign_repos = [];
        $scope.form_fields = {'tagMode': 'Repo'};

        initController();

        function initController() {
            get_this_user();
            load_tag_definitions();
            load_categorized_tags(26);
            $scope.assigned_tag_definition = 26;
            get_repos();
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
                        vm.loading = false;
                      }
                    , function(err) {
                        $scope.status = 'Error loading data: ' + err.message;
                        vm.loading = false;
                      }
                );
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

        $scope.delete_tagging = function(_id) {
            console.log('[126] id: ' + _id);
            // get_this_user();
        }

        $scope.submit_auto_tag = function() {
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
            $scope.form_fields['username'] = $scope.profile.username;
            // console.log($$("tags_tree").getSelectedId());
            // console.log($$("tags_tree").getChecked());

            CategorizedTagsService
                ._insert_categorizedtags($scope.form_fields)
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
                        // clear status message after five seconds
                        $timeout(function() {
                            $scope.status = '';
                        }, 5000);
                    }
                );
        }
    }
})();
