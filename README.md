[DRAFT SUBJECT TO UPDATE]

MIST rewrite v2

Summary:
 - Uses current MIST MySQL datasource
 - Installed under /opt/mist_base (installation may be automated later)
 - Back end uses Python v2.7
   - Custom environment built under CentOS v6.x
   - Included as virtualenv; install modules with pip using requirements.txt
 - Front end SPA uses AngularJS v1.5.x

Installation
 - Clone into /opt/mist_base
 - Directories are as follows:
   - app: the Python/Flask-based scripts/API endpoints
   - certificates: used for database connectivity
   - env: the custom Python runtime/environment
   - static: HTML content, JS libraries, AngularJS SPA app
 
Start up:
 (for development)
 $ cd /opt/mist_base/app
 $ uwsgi --py-autoreload 1 -s 0.0.0.0:8080 --protocol=http -w wsgi --static-map /static=/opt/mist_base/static
 