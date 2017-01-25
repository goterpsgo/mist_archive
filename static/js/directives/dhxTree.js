/**
 * Created by jtseng on 1/25/17.
 */

(function () {
    'use strict';

    angular
        .module('app')
        .directive('dhxTree', Directive);

    function Directive(DhxUtils) {
        return {
            restrict: 'E',
            require: 'dhxTree',
            controller: function () {
            },
            scope: {
            /**
             * Tree will be accessible in controller via this scope entry
             * after it's initialized
             */
            dhxTree: '=',
            /**
             * Please refer to the following link for format:
             * http://docs.dhtmlx.com/tree__syntax_templates.html#jsonformattemplate
             */
            dhxJsonData: '=',
            /**
             * [{type: <handlerType>, handler: <handlerFunc>}]
             * where type is 'onSomeEvent'
             * Events can be seen at: http://docs.dhtmlx.com/api__refs__dhtmlxtree_events.html
             * Optional
             */
            dhxHandlers: '=',
            /**
             * Not an exhaustive list of enablers... feel free to add more.
             * Optionals!
             */
            dhxEnableCheckBoxes: '=',
            dhxEnableDragAndDrop: '=',
            dhxEnableHighlighting: '=',
            dhxEnableThreeStateCheckboxes: '=',
            dhxEnableTreeLines: '=',
            dhxEnableTreeImages: '=',
            /**
             * preLoad and postLoad callbacks to controller for additional
             * customization power.
             */
            dhxConfigureFunc: '=',
            dhxOnDataLoaded: '=',

            dhxContextMenu: '='
            },
            link: function (scope, element/*, attrs, treeCtrl*/) {
            //noinspection JSPotentiallyInvalidConstructorUsage
            var tree = new dhtmlXTreeObject({
              parent: element[0],
              skin: "dhx_skyblue",
              checkbox: true,
              image_path: DhxUtils.getImagePath() + 'dhxtree_material/'
            });

            scope.dhxTree ? scope.dhxTree = tree : '';

            scope.dhxContextMenu ? tree.enableContextMenu(scope.dhxContextMenu) : '';
            scope.$watch(
              "dhxContextMenu",
              function handle( newValue) {
                tree.enableContextMenu(newValue);
              }
            );

            // Additional optional configuration
            tree.enableCheckBoxes(scope.dhxEnableCheckBoxes);

            tree.enableDragAndDrop(scope.dhxEnableDragAndDrop);
            tree.enableHighlighting(scope.dhxEnableHighlighting);
            tree.enableThreeStateCheckboxes(scope.dhxEnableThreeStateCheckboxes);
            tree.enableTreeImages(scope.dhxEnableTreeImages);
            tree.enableTreeLines(scope.dhxEnableTreeLines);
            // Letting controller add configurations before data is parsed

            if (scope.dhxConfigureFunc) {
              scope.dhxConfigureFunc(tree);
            }
            // Finally parsing data
            tree.parse(scope.dhxJsonData, "json");

            // Letting controller do data manipulation after data has been loaded

            if (scope.dhxOnDataLoaded) {
              scope.dhxOnDataLoaded(tree);
            }
            DhxUtils.attachDhxHandlers(tree, scope.dhxHandlers);
            DhxUtils.dhxUnloadOnScopeDestroy(scope, tree);
            }
        };

    }


})();
