#!/bin/bash

export PYTHONPATH=`pwd`

uwsgixml="/home/mafia/workspace/horoscopes_server/uwsgi.xml"
touchfile="/home/mafia/workspace/horoscopes_server/bin/touch_reload_uwsgi"
touchlogfile="/home/mafia/workspace/horoscopes_server/bin/touch_reopen_log"

/usr/bin/uwsgi --uid mafia -x ${uwsgixml} --touch-reload=${touchfile} --touch-logreopen=${touchlogfile} --listen 4096
