# Help desk

Software engineering task.

## Requirements

* python
* django
* xlrd (required for importing *.xlsx)
* python-pygraphviz (required only for rendering models graph)

## Running

```
python manage.py runserver
```

## First run

Before first run, reinit.sh must be ran

```
./reinit.sh
```

## Defaults

Default login information

```
ID: client, PW: client

ID: admin, PW: admin
```

## Import

Import of xlsx/xls is possible, using administration menu.
Imported users get their login information set to:

```
ID: userEmail@email.com, 

PW: FirstName
```


