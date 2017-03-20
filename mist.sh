#!/usr/bin/env sh
# Source function library.
. /etc/rc.d/init.d/functions
 
if [ -f /etc/sysconfig/nginx ]; then
    . /etc/sysconfig/nginx
fi


MIST_HOME=/opt/mist/mist_base
USER=mist

APP_HOME=$MIST_HOME/app
ENV_HOME=$MIST_HOME/env
NGINX_HOME=$MIST_HOME/nginx/default

PROG=mist
NGINX_NAME=nginx
NGINX_CONFFILE=$NGINX_HOME/conf/$NGINX_NAME.conf
NGINX_LOCKFILE=/var/lock/subsys/$NGINX_NAME
NGINX_PIDFILE=/tmp/$NGINX_NAME.pid
NGINX_BIN=$NGINX_HOME/sbin/$NGINX_NAME

UWSGI_NAME=uwsgi
UWSGI_LOCKFILE=/var/lock/subsys/mist
UWSGI_PIDFILE=/tmp/mist_app.pid
UWSGI_BIN=$ENV_HOME/bin/$UWSGI_NAME

SCRIPTNAME=/etc/init.d/$PROG

PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin:$NGINX_HOME/sbin:$ENV_HOME/bin

start() {
        # Starting web server
		echo -n "Starting $NGINX_NAME... "

		pidof $NGINX_NAME >/dev/null
		if [ "$?" = 0 ] ; then
			echo "$NGINX_NAME (pid `pidof $NGINX_NAME`) already running."
			exit 1
		else
		    echo "$NGINX_BIN -c $NGINX_CONFFILE"
		    $NGINX_BIN -c $NGINX_CONFFILE
		fi

		if [ "$?" != 0 ] ; then
			echo " failed"
			exit 1
		else
			echo " done"
		fi

        # Starting application server
		echo -n "Starting $UWSGI_NAME... "

		pidof $UWSGI_NAME >/dev/null
		if [ "$?" = 0 ] ; then
			echo "$UWSGI_NAME (pid `pidof $UWSGI_NAME`) already running."
        else
	    echo "$UWSGI_BIN --py-autoreload 1 --master --socket=/tmp/mist_app.sock --pidfile=/tmp/mist_app.pid --module=wsgi --honour-stdin --chdir=$APP_HOME --threads=1 --virtualenv=$ENV_HOME --die-on-term --uid $USER --gid $USER"
            $UWSGI_BIN --py-autoreload 1 --master --socket=/tmp/mist_app.sock --pidfile=/tmp/mist_app.pid --module=wsgi --honour-stdin --chdir=$APP_HOME --threads=1 --virtualenv=$ENV_HOME --die-on-term --uid $USER --gid $USER --logto=/opt/mist_base/log/mist_app.log > /dev/null 2>&1 &
		fi

		if [ "$?" != 0 ] ; then
			echo " failed"
			exit 1
		else
			echo " done"
		fi
}

stop() {

        # Stopping application server
		echo -n "Stoping $UWSGI_NAME... "

		kill -9 `pidof $UWSGI_NAME` 2>/dev/null
		rm /tmp/mist_app.sock

		if [ "$?" != 0 ] ; then
			echo " failed"
		else
			echo " done"
		fi

        # Stopping web server
		echo -n "Stoping $NGINX_NAME... "

		kill -9 `pidof $NGINX_NAME` 2>/dev/null

		if [ "$?" != 0 ] ; then
			echo " failed"
		else
			echo " done"
		fi
}

restart() {
		$SCRIPTNAME stop
		sleep 1
		$SCRIPTNAME start
}

# See how we were called.
case "$1" in
    start)
        start
        ;;
    stop)
        stop
        ;;
#    status)
#        rh_status
#        RETVAL=$?
#        ;;
    restart)
        stop
        start
        ;;
    *)
        echo $"Usage: $prog {start|stop|restart}"
        RETVAL=2
esac
exit $RETVAL
