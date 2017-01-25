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
        $scope.treeData = {
          "id": 0,
          "item": [
            {
              "id": "dataCmps",
              "text": "Data",
              "item": [
                {
                  "id": "Grid",
                  "text": "Grid"
                },
                {
                  "id": "Tree",
                  "text": "Tree"
                }
              ]
            },
            {
              "id": "Windows",
              "text": "Windows"
            },
            {
              "id": "Layout",
              "text": "Layout"
            }
          ]
        };

        initController();

        function initController() {
            load_tag_definitions();
            load_categorized_tags(23);
        }

        function load_tag_definitions() {
            vm.loading = true;
            TagDefinitionsService
                ._get_tagdefinitions()
                .then(
                    function(results) {
                        console.log('[25] Got here:');
                        console.log(results.tag_definitions);
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
            console.log('[40] ID: ' + _id);
            CategorizedTagsService
                ._get_categorizedtags(_id)
                .then(
                      function(results) {
                        $scope.categorized_tags = results;
                      }
                    , function(err) {
                        $scope.status = 'Error loading data: ' + err.message;
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

        $scope.treeDataLoaded = function (tree) {
          console.log('Data has been loaded!');
        };

        $scope.treeHandlers = [
          {
            type: "onClick",
            handler: function (id) {
              console.log('You have clicked \'' + id + '\'');
            }
          }
        ];

        $scope.contextMenu = {};
    }
})();
