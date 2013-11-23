#!/bin/sh
rm db -f && ./manage.py syncdb --noinput && ./manage.py createdata
