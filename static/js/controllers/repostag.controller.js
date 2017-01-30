(function () {
    'use strict';
 
    angular
        .module('app')
        .controller('Repostag.IndexController', Controller);

    function Controller($scope, TagDefinitionsService, CategorizedTagsService) {
        var vm = this;
        $scope.tag_definitions = {};
        $scope.assigned_tag_definition = {"value": 23};
        $scope.categorized_tags = {};
        $scope.treeData = {"value": "Loading..."};
        $scope.tags_tree = null;

        initController();

        function initController() {
            load_tag_definitions();
            load_categorized_tags(26);
            $scope.assigned_tag_definition = 26;
            // $scope.tags_tree = $$("tags_tree");
            console.log('[23] initController()');
            // console.log($scope.tags_tree);
        }

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

        function load_categorized_tags(_id) {
            vm.loading = true;
            CategorizedTagsService
                ._get_categorizedtags(_id)
                .then(
                      function(results) {
                        $scope.treeData = results.treeData;
                        vm.loading = false;
                      }
                    , function(err) {
                        $scope.status = 'Error loading data: ' + err.message;
                        vm.loading = false;
                      }
                )
            ;
        };

        $scope.load_tags = function() {
            load_categorized_tags($scope.assigned_tag_definition.id);
        }

        $scope.submit_auto_tag = function() {
            console.log('[59] Got here');
        }

        $scope.do_this = function(id, details) {
            console.log('[65] do_this(): ');
            console.log($$("tags_tree").getSelectedId());
        }
    }
})();
