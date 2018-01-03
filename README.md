Notes From Below
================

Django site for managing an online publication.

## Setup

`pip install -r requirements.txt`

Set the following environment variables within the virtualenv:

* `POSTGRES_PASSWORD`: the passowrd
* `DJANGO_SECRET_KEY`: the `SECRET_KEY` used by Django
* `HOSTNAME`: e.g., 'notesfrombelow.org'

`cd django && ./manage.py runserver`
