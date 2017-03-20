// http://www.jvandemo.com/how-to-configure-your-angularjs-application-using-environment-variables/
(function (window) {
  window.__env = window.__env || {};

  // API url
  window.__env.api_url = 'https://10.11.1.239';

  // Port
  window.__env.port = '8444';

  // Base url
  window.__env.base_url = '/';

  // Whether or not to enable debug mode
  // Setting this to false will disable console output
  window.__env.enable_debug = true;
}(this));
