Notes From Below
================

Django site for managing an online publication.

## Setup

`pip install -r requirements.txt`

Set the following environment variables within the virtualenv:

* `POSTGRES_PASSWORD`: the passowrd
* `DJANGO_SECRET_KEY`: the `SECRET_KEY` used by Django
* `ALLOWED_HOST`: e.g., 'notesfrombelow.org'

To run:

`./django/manage.py makemigrations journal cms`
`./django/manage.py migrate`
`./django/manage.py createsuperuser`

Finally:

`./django/manage.py runserver`
