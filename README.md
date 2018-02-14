Notes From Below
================

Django site for managing an online publication.

## Setup

Within a virtualenv, run the following commands, in order:

```bash
pip install -r requirements.txt
./django/manage.py makemigrations journal cms
./django/manage.py migrate
./django/manage.py createsuperuser
./django/manage.py loaddata initial_fixtures.json
```

Finally:

`./django/manage.py runserver`

You can find the admin interface at <http://localhost:8000/sudo/> (for the
superuser) or <http://localhost:8000/editor/> (the link to give to editors).
You can create users with editor permissions via the /sudo/ admin site:
set `is_staff` to True, and give them any necessary permissions (there will
be a permission group eventually, but for now you'll have to select them
manually).

None of the links in the menu will work. You'll have to create the 4 categories
(under the journal app) and the 2 pages (under the cms app).

## Deploying in production

To deploy in production with Postgres, a custom secret key, and DEBUG=False,
set the following environment variables within the virtualenv:

* `POSTGRES_PASSWORD`: the password for PostgreSQL
* `DJANGO_SECRET_KEY`: the `SECRET_KEY` used by Django (set to a random string)
* `ALLOWED_HOST`: e.g., 'notesfrombelow.org'
