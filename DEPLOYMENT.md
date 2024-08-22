# Deployment

(Copied from the left-in-the-bay repo)

This document is only for me, Wendy. My goal is to document how I deployed this horrific app because I know I will forget something important at a crucial juncture. You do not need to read this if you're merely curious about how this app works. Please do not read this.

**New deployment as of August 21, 2024**

## Server details

Running on a $6/month Digital Ocean droplet named 'nfb'. 1GB RAM, 25GB disk. Weekly backups. The cheapest possible. Might need to upgrade at some point.

Logging in as root with ssh keys (no password). Using .ssh/config to simplify (IP address, 'nfb').

## Server setup

Follow the instructions in here up until the pip install part

https://www.digitalocean.com/community/tutorials/how-to-set-up-django-with-postgres-nginx-and-gunicorn-on-ubuntu#creating-the-postgresql-database-and-user

Generate a postgres password and note it down somewhere.

Then follow the instructions in here to get the bare git repo situation set up:

<https://daveceddia.com/deploy-git-repo-to-server/>

The post-receive hook should look like this:

```
#!/bin/sh

# Check out the files
git --work-tree=/var/www/notesfrombelow --git-dir=/root/notesfrombelow/bare_repo.git checkout -f
```

Then run `chmod +x` and `mkdir /var/www/notesfrombelow`.

Now, in the local repo, run `git remote add production nfb:/root/notesfrombelow/bare_repo.git` and push to the bare repo (`git push production master`).

Now go back to the Digital Ocean tutorial and run `pip install -r requirements.txt` from /var/www/notesfrombelow/. We need to manually get psycopg2.

### Updating settings

Now we need to make sure settings allows for both a local, debug-on mode, and production, debug-off mode. (This is already done in the code that's been committed to this repo; I just want to document what I did.) Check settings.py in bookmarker or something but make sure there's a `postgres_password = os.environ.get('POSTGRES_PASSWORD')` somewhere in there, and and if/else switch for postgres/sqlite depending on whether that exists.

### Environment variables

Add the following lines to env/bin/activate:

```
. variables
export POSTGRES_PASSWORD
```

and then env/bin/variables looks like this:

```
POSTGRES_PASSWORD='(saved password)'
```

### Database

Now going back to the DO tutorial (make sure that we deactivate and reactivate, or like update .bashrc and then log out and log back in to trigger the env variable) we run ```python manage.py makemigrations blog cms journal uploads```, then migrate, then create superuser.

If we run into an error of the form

```
django.db.migrations.exceptions.MigrationSchemaMissing: Unable to create the django_migrations table (permission denied for schema public
LINE 1: CREATE TABLE "django_migrations" ("id" integer NOT NULL PRIM...
```

then go back into `sudo -u postgres psql` and run `ALTER DATABASE notesfrombelow OWNER TO notesfrombelow` which hopefully will fix it. idk why.

### Gunicorn

Next, create the gunicorn socket file. (It should have been installed outside of requirements.txt when following the DO tutorial.) The gunicorn.service file should look like this (at /etc/systemd/system/gunicorn.socket):

```
[Unit]
Description=gunicorn daemon
Requires=gunicorn.socket
After=network.target

[Service]
User=root
Group=root
WorkingDirectory=/var/www/notesfrombelow/src
EnvironmentFile=/root/notesfrombelow/env/bin/variables
ExecStart=/root/notesfrombelow/env/bin/gunicorn \
        --access-logfile - \
        --workers 3 \
        --bind unix:/run/gunicorn.sock \
        notesfrombelow.wsgi:application

[Install]
WantedBy=multi-user.target
```

Now run `systemctl start gunicorn`.

### Nginx

Make sure nginx.conf has `user root` on top (helpful to avoid permissions issues with the media and static-collected dirs).

Nginx conf file should look like this (TODO)

```
server {
    listen 80;
    listen [::]:80;
    server_name notesfrombelow.dellsystem.me notesfrombelow.org www.notesfrombelow.org;
    return 302 https://$server_name$request_uri;
}


server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    ssl_certificate /etc/ssl/cert.pem;
    ssl_certificate_key /etc/ssl/key.pem;

    server_name notesfrombelow.org www.notesfrombelow.org;

    location = /favicon.ico {
	    alias /var/www/notesfrombelow/src/static-collected/favicon.ico;
    }

    location = /favicon-32x32.png {
	    alias /var/www/notesfrombelow/src/static-collected/favicon-32x32.png;
    }

    location = /favicon-16x16.png {
	    alias /var/www/notesfrombelow/src/static-collected/favicon-16x16.png;
    }


    location = /safari-pinned-tab.svg {
	    alias /var/www/notesfrombelow/src/static-collected/safari-pinned-tab.svg;
    }
    location = /site.webmanifest {
	    alias /var/www/notesfrombelow/src/static-collected/site.webmanifest;
    }
    location = /apple-touch-icon.png {
	    alias /var/www/notesfrombelow/src/static-collected/apple-touch-icon.png;
    }

    location /static/ {
        alias /var/www/notesfrombelow/src/static-collected/;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/run/gunicorn.sock;
    }
}
```

## Domain name setup

Use cloudflare and use the IP address of the new server. Do SSL through cloudflare (full mode). Make sure to generate an origin certificate and install the cert and key on the remote server (/etc/ssl/cert.pem, /etc/ssl/key.pem).

## Data migration

If the result of dumpdata is too large to use with loaddata, try deleting older version history (see <https://django-reversion.readthedocs.io/en/latest/commands.html>) and breaking it up into individual apps/groups of apps. eg:

```
python src/manage.py deleterevisions journal.Article --keep=3 --days=90
python src/manage.py dumpdata admin auth contenttypes --natural-foreign -o backups/admin-auth-contenttypes.json.gz
python src/manage.py dumpdata sessions --natural-foreign -o backups/sessions.json.gz
python src/manage.py dumpdata blog --natural-foreign -o backups/blog.json.gz
python src/manage.py dumpdata reversion --natural-foreign -o backups/reversion.json.gz
python src/manage.py dumpdata journal --natural-foreign -o backups/journal.json.gz
python src/manage.py dumpdata cms --natural-foreign -o backups/cms.json.gz
python src/manage.py dumpdata blog --natural-foreign -o backups/blog.json.gz
python src/manage.py dumpdata uploads --natural-foreign -o backups/uploads.json.gz
```

Then scp the files over and run loaddata one by one.

## Maintenance

Other commands we might have to run in the course of managing this:

### Static files

```
python src/manage.py collectstatic --noinput
```

Do this in /var/www/notesfrombelow whenever we change static files


### Remarkdown

If something changes with the markdown extensions or whatever and we need to re-cache all the generated HTML, run:

```
python src/manage.py cms_remarkdown
python src/manage.py journal_remarkdown
```

### Backups

Beyond DO's built-in weekly backups, we also want to automatically back up the database and media files to Digital Ocean Spaces. We're currently using my personal spaces to save money. Weekly backups are configured via a cron job.

Install rclone with `apt install rclone`.

Set up the rclone conf file (~/.config/rclone/rclone.conf):

```
[spaces]
type = s3
provider = DigitalOcean
env_auth = false
endpoint = sfo2.digitaloceanspaces.com
access_key_id = (omitted)
secret_access_key = (omitted)
```

crontab should have something like

```
0 7 * * 1 bash /root/notesfrombelow/weeklybackup.sh
```

weeklybackup.sh should look like

```
#!/bin/bash
source /root/notesfrombelow/env/bin/activate
cd /var/www/notesfrombelow
db_filename="backups/nfb_database_$(date +%F).json.gz"
python /var/www/notesfrombelow/src/manage.py dumpdata --natural-foreign -o $db_filename
rclone copy $db_filename spaces:dellsystem-backups/notes-from-below/database
media_filename="backups/nfb_media_$(date +%F).tar.gz"
tar czf $media_filename media/
rclone copy $media_filename spaces:dellsystem-backups/notes-from-below/media
rm $db_filename
rm $media_filename
```

chmod +x then test it out.
