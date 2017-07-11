(function () {
    'use strict';
 
    angular
        .module('app')
        .controller('Tagactivities.IndexController', Controller);

    function Controller($scope, AssetsService) {
        var vm = this;

        initController();

        function initController() {
            load_tagged_assets();
        }

        function load_tagged_assets() {
            // Service will not trigger unless a repo is supplied or category and search string are supplied
            AssetsService
                ._get_tagged_assets($scope.search_form)
            .then(
                function(result) {
                    $scope.column_names = [
                        {
                          "name": "Date"
                          , "displayName": "Timestamp"
                          , "field": "timestamp"
                          , "sort": {"direction": "asc", "priority": 0}
                        }, {
                          "name": "Asset ID"
                          , "displayName": "Asset ID"
                          , "field": "assetID"
                          , "width": 80
                        }, {
                          "name": "Tag ID"
                          , "displayName": "Tag ID"
                          , "field": "tagID"
                          , "width": 80
                        }, {
                          "name": "Tag Mode"
                          , "displayName": "Tag Mode"
                          , "field": "tagMode"
                        }, {
                          "name": "Tagged By"
                          , "displayName": "Tagged By"
                          , "field": "taggedBy"
                        }
                    ];

                    $scope.grid_options = {
                        columnDefs: $scope.column_names
                    };
                    $scope.grid_options.data = result.tagged_assets_list;
                  }
                , function(err) {
                    $scope.status = 'Error loading data: ' + err.message;
                  }
            );
        }

    }
})();
