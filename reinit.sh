#!/bin/sh
rm help_desk/db -f && ./manage.py syncdb --noinput && ./manage.py createdata
