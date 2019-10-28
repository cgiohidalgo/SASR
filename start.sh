#!/bin/bash
#source  ./venv/bin/activate
#gunicorn --name sasr --bind 0.0.0.0:80 app:app --daemon &
source /var/www/sasr/venv/bin/activate
#kill -9 `ps -A | grep gunicorn | awk '{ print $1 }'`
gunicorn --name sasr --workers=4 --threads=2 --bind 0.0.0.0:80 app:app --daemon 

