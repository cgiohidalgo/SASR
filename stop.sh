#!/bin/sh
kill -9 `ps -A | grep gunicorn | awk '{ print $1 }'`
