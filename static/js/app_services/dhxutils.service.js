/**
 * Created by jtseng on 1/25/17.
 */

(function () {
    'use strict';

    angular
        .module('app')
        .factory('DhxUtils', Service);

    function Service() {
        var _imgPath = "static/img/";

        /**
         * @param dhxObject
         * @param dhxHandlers
         */
        var attachDhxHandlers = function (dhxObject, dhxHandlers) {
          (dhxHandlers || [])
            .forEach(function (info) {
              dhxObject.attachEvent(info.type, info.handler);
            });
        };

        var getImagePath = function () {
          return _imgPath;
        };

        var setImagePath = function (imgPath) {
          _imgPath = imgPath;
        };

        /**
         * I hope to never resort to using that
         */
        var createCounter = function () {
          var current = -1;
          return function () {
            current++;
            return current;
          };
        };

        var removeUndefinedProps = function(obj) {
          for (var prop in obj) {
            if (obj.hasOwnProperty(prop) && obj[prop] === undefined) {
              delete obj[prop];
            }
          }
        };

        var dhxDestroy = function (dhxObj) {
          var destructorName =
            'destructor' in dhxObj
              ? 'destructor'
              :
              ('unload' in dhxObj
                ? 'unload'
                : null);

          if (destructorName === null) {
            console.error('Dhtmlx object does not have a destructor or unload method! Failed to register with scope destructor!');
            return;
          }

          dhxObj[destructorName]();
        };


        var dhxUnloadOnScopeDestroy = function (scope, dhxObj) {
          var destructorName =
            'destructor' in dhxObj
              ? 'destructor'
              :
              ('unload' in dhxObj
                ? 'unload'
                : null);
          if (destructorName === null) {
            console.error('Dhtmlx object does not have a destructor or unload method! Failed to register with scope destructor!');
            return;
          }

          scope.$on(
            "$destroy",
            function (/*event*/) {
              dhxObj[destructorName]();
            }
          );
        };

        return {
          attachDhxHandlers: attachDhxHandlers,
          getImagePath: getImagePath,
          setImagePath: setImagePath,
          createCounter: createCounter,
          removeUndefinedProps: removeUndefinedProps,
          dhxUnloadOnScopeDestroy: dhxUnloadOnScopeDestroy,
          dhxDestroy: dhxDestroy
        };
    }
})();


