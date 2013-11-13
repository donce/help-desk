#!/bin/sh
rm db && ./manage.py syncdb --noinput && ./manage.py createdata
