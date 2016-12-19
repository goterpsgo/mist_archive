[DRAFT SUBJECT TO UPDATE]

MIST rewrite v2

Summary:
 - Uses current MIST MySQL datasource
 - Installed under ``/opt/mist_base`` (installation may be automated later)
 - Back end uses Python v2.7.13
   - Custom environment built under CentOS v6.x
   - Included as virtualenv; install modules with pip using requirements.txt
 - Front end SPA uses AngularJS v1.5.x
   - NOTE: upgrade to v1.6.x will require refactoring some code

Installation
 - Clone into /opt/mist_base
   - If needed, install dependencies using pip: ``pip install -r /opt/mist_base/requirements.txt``
     - To upgrade dependencies use: ``pip install --upgrade -r /opt/mist_base/requirements.txt``
     - (To up grade pip use: ``pip install --upgrade pip``)
 - Directories are as follows:
   - app: the Python/Flask-based scripts/API endpoints
   - certificates: used for database connectivity
   - env: the custom Python runtime/environment
   - static: HTML content, JS libraries, AngularJS SPA app
   - nginx: web server binary compiled from source. Includes conf file.
 
Start up

(for development)
```
$ sudo /opt/mist_base/mist.sh start
$ sudo /opt/mist_base/mist.sh restart
$ sudo /opt/mist_base/mist.sh stop
```

(Deprecated but retained for reference) Running the application server by itself:
Assuming you're running everything using a generic generic environment:
1. Start the web server:
 ```
 $ /opt/mist_base/nginx/default/sbin/nginx -c /opt/mist_base/nginx/default/conf/nginx.conf
 ```
2. Start the application server:
 ```
 $ /opt/mist_base/env/bin/uwsgi --master --chdir=/opt/mist_base/app --socket=/tmp/mist_app.sock --threads=5 --die-on-term \
   --pidfile=/tmp/mist_app.pid-module=wsgi --virtualenv=/opt/mist_base/env --honour-stdin \
   --py-autoreload 1 --logto=/opt/mist_base/log/mist_app.log
 ```

(Deprecated but retained for reference) Running the application server by itself: 
 ```
 $ uwsgi --wsgi-file /opt/mist_base/app/mist_main.py  -s 0.0.0.0:8080 --protocol=http -w wsgi --static-map /static=/opt/mist_base/static --honour-stdin
 ```
 - honour-stdin param can be omitted if you don't need to see results sent to stdout.
 - wsgi-file param must reference script with either an application declaration or reference to Flask().
