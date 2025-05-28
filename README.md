# pepysdiary

[![Build Status](https://github.com/philgyford/pepysdiary/actions/workflows/test.yml/badge.svg)](https://github.com/philgyford/pepysdiary/actions/workflows/test.yml)
[![codecov](https://codecov.io/gh/philgyford/pepysdiary/branch/main/graph/badge.svg?token=GD97K3Q26Z)](https://codecov.io/gh/philgyford/pepysdiary)
[![Code style: prettier](https://img.shields.io/badge/code_style-prettier-ff69b4.svg?style=flat-square)](https://github.com/prettier/prettier)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)

Code for [www.pepysdiary.com](http://www.pepysdiary.com/).

Pushing to `main` will run the commit through [this GitHub Action](https://github.com/philgyford/pepysdiary/actions/workflows/main.yml) to run tests. If it passes, it will be deployed automatically to the website.

## Changing Python version

If changing the Python version you'll need to change it in:

- `.pre-commit-config.yaml`
- `.python-version` (for uv)
- `pyproject.toml` (in `project`, `tool.ruff` and `tool.uv.pip`)

For local development we use Docker. The live site is on an Ubuntu 22 VPS.

## Local development setup

We use three Docker containers: Postgres database, optional Redis cache, and building assets.

We use [uv](https://docs.astral.sh/uv/) to create a virtual environment on the host machine (i.e. not in Docker) to run Django development webserver.

### 1. Create a .env file

Copy `.env.dist` to `.env` and alter any necessary settings.

### 2. Set up a local domain name

Open your `/etc/hosts` file in a terminal window by doing:

    $ sudo vim /etc/hosts

Enter your computer's password. Then add this line somewhere in the file and save:

    127.0.0.1 www.pepysdiary.test

### 3. Build the Docker containers

Download, install and run Docker Desktop.

In same directory as this README, build the containers:

    $ docker compose build

Then start up the web, assets and database containers:

    $ docker compose up

There are three containers:

- `pepysdiary_db`: the postgres server
- `pepysdiary_assets`: the front-end assets builder
- `pepysdiary_redis`: the redis server (for optional caching)

All the repository's code is mirrored in the web and assets containers in the `/code/` directory.

### 4. Set up the database

Once Docker's running, showing the logs, open another terminal window/tab.

There are two ways we can populate the database. First we'll create an empty one, and second we'll populate it with a dump of data from the live site.

#### 4a. An empty database

The `build` step will create the database and run the initial Django migrations.

Then create a superuser:

    $ ./run manage createsuperuser

(See below for more info on the `./run` script.)

#### 4b. Use a dump from the live site

Dump a database on the server with:

    $ pg_dump -h localhost -U username -d dbname -Fc -b -f ~/dump.sql

SCP that to this local directory with:

    $ scp username@your.vps.domain.com:/home/username/dump.sql .

Drop the existing dev database:

    $ ./run psql -d postgres
    # DROP DATABASE pepys WITH (FORCE);
    # CREATE DATABASE pepys;
    # GRANT ALL PRIVILEGES ON DATABASE pepys TO pepys;
    # \q

Then copy the dump into Docker and load it into the database:

    $ docker cp dump.sql pepys_db:/tmp/
    $ docker exec -i pepys_db pg_restore -h localhost -U pepys -d pepys -j 2 /tmp/dump.sql

#### 5. uv environment

Create a virtual env and install Python dependencies using `uv`:

    $ uv sync

The webserver process is run on your local machine, not in Docker:

    $ run runserver

See the `./run` script for more shortcuts.

##### 5a. Updating dependencies

The live site currently doesn't use `uv`, so we need to keep `requirements.txt`
updated if we change anything:

    $ uv export --quiet --format requirements-txt --output-file requirements.txt

#### 5. Vist and set up the site

Then go to http://www.pepysdiary.test:8000 and you should see the site.

Log in to the [Django Admin](http://www.pepysdiary.test:8000/backstage/), go to the "Sites" section and change the one Site's Domain Name to `www.pepysdiary.test:8000` and the Display Name to "The Diary of Samuel Pepys", if it's not already.

## Ongoing work

### Docker

Whenever you come back to start work you need to start the containers up again by doing this from the project directory:

    $ docker compose up

When you want to stop the server, then this from the same directory:

    $ docker compose down

You can check if anything's running by doing this, which will list any Docker processes:

    $ docker ps

See details on the `./run` script below for running things inside the containers.

### pre-commit

Install [pre-commit](https://pre-commit.com) to run `.pre-commit-config.yml` automatically when `git commit` is done.

## Front-end assets

Gulp is used to build the final CSS and JS file(s), and watches for changes in the `pepysdiary_assets` container. Node packages are installed and upgraded using `yarn` (see `./run` below).

## The ./run script

The `./run` script makes it easier to run things that are within the Docker containers. This will list the commands available, which are outlined below:

    $ ./run

### `./run tests`

Runs all the Django tests. If it complains you might need to do `./run manage collecstatic` first.

Run a folder, file, or class of tests, or a single test, something like this:

    $ ./run tests tests.core
    $ ./run tests tests.core.test_views
    $ ./run tests tests.core.test_views.HomeViewTestCase
    $ ./run tests tests.core.test_views.HomeViewTestCase.test_response_200

### `./run coverage`

Run all the tests with coverage. The HTML report files will be at `htmlcov/index.html`.

### `./run psql`

Conects to PosgreSQL with psql. Add any required arguments on the end. Uses the `hines` database unless you specify another like:

    $ ./run psql -d databasename

### `./run yarn:outdated`

List any installed Node packages (used for building front end assets) that are outdated.

### `./run yarn:upgrade`

Update any installed Node packages that are outdated.

## Removing users and annotations from the local database

What I did to create a version of the database without personal information. After exporting the live database and importing into the local Docker database:

    $ ./run psql
    pepysdiary=# TRUNCATE django_comments, django_comment_flags, auth_user, annotations_annotation, membership_person;
    pepysdiary=# UPDATE diary_entry SET comment_count=0;
    pepysdiary=# UPDATE encyclopedia_topic SET comment_count=0;
    pepysdiary=# UPDATE indepth_article SET comment_count=0;
    pepysdiary=# UPDATE letters_letter SET comment_count=0;
    pepysdiary=# UPDATE news_post SET comment_count=0;
    pepysdiary=# \q
    $ ./run manage createsuperuser

Then logged into Django Admin and changed the Site "Domain name" to `www.pepysdiary.test:8000`.

Then dumped that modified database:

    $ docker exec -i pepys_db pg_dump pepysdiary -U pepysdiary -h localhost | gzip > pepys_dump.gz

## VPS set-up

The complete set-up of an Ubuntu VPS is beyond the scope of this README. Requirements:

- Local postgresql
- Local redis (for caching)
- pipx, virtualenv and pyenv
- gunicorn
- nginx
- systemd
- cron

### 1. Create a database

    username$ sudo su - postgres
    postgres$ createuser --interactive -P
    postgres$ createdb --owner pepys pepys
    postgres$ exit

### 2. Create a directory for the code

    username$ sudo mkdir -p /webapps/pepys/
    username$ sudo chown username:username /webapps/pepys/
    username$ mkdir /webapps/pepys/logs/
    username$ cd /webapps/pepys/
    username$ git clone git@github.com:philgyford/pepysdiary.git code

### 3. ## Install python version, set up virtualenv, install python dependencies

    username$ pyenv install --list  # All those available to install
    username$ pyenv versions        # All those already installed and available
    username$ pyenv install 3.10.8  # Whatever version we're using

Make the virtual environment and install pip-tools:

    username$ cd /webapps/pepys/code
    username$ virtualenv --prompt pepys venv -p $(pyenv which python)
    username$ source venv/bin/activate
    (pepys) username$ python -m pip install pip-tools

Install dependencies from `requirements.txt`:

    (pepys) username$ pip-sync

### 4. Create `.env` file

    (pepys) username$ cp .env.dist .env

Then fill it out as required.

### 5. Set up database

Either do `./manage.py migrate` and `./manage.py createsuperuser` to create a new database, or import an existing database dumbp.

### 6. Set up gunicorn with systemd

Symlink the files in this repo to correct location for systemd:

    username$ sudo ln -s /webapps/pepys/code/conf/systemd_gunicorn.socket /etc/systemd/system/gunicorn_pepys.socket
    username$ sudo ln -s /webapps/pepys/code/conf/systemd_gunicorn.service /etc/systemd/system/gunicorn_pepys.service

Start the socket:

    username$ sudo systemctl start gunicorn_pepys.socket
    username$ sudo systemctl enable gunicorn_pepys.socket

Check the socket status:

    username$ sudo systemctl status gunicorn_pepys.socket

Start the service:

    username$ sudo systemctl start gunicorn_pepys

### 5. Set up nginx

Symlink the file in this repo to correct location:

    username$ sudo ln -s /webapps/pepys/code/conf/nginx.conf /etc/nginx/sites-available/pepys

Enable this site:

    username$ sudo ln -s /etc/nginx/sites-available/pepys /etc/nginx/sites-enabled/pepys

Remove the default site if it's not already:

    username$ sudo rm /etc/nginx/sites-enabled/default

Check configuration before (re)starting nginx:

    username$ sudo nginx -t

Start nginx:

     username$ sudo service nginx start

### 6. Set up cron for management commands

    username$ crontab -e

Add this:

    # pepys - fetch some content from Wikipedia
    10 3,4,5,6 * * * /webapps/pepys/code/venv/bin/python /webapps/pepys/code/manage.py fetch_wikipedia --num=30 > /dev/null 2>&1

### Other stuff

- Allow service restarts without a password, so that GitHub Actions autodeploy works
- Set up Let's Encrypt for the domain

## Bootstrap

W're using Boostrap SASS to generate a custom set of Bootstrap CSS. Comment/uncomment lines in `assets/sass/_bootstrap_custom.scss` to change which parts of Bootstrap's CSS are included in the generated CSS file.

### Bootstrap's JavaScript

We must manually download a custom version of Bootstrap's JavaScript file.

Instead of steps 2 and 3 you can hopefully upload the `assets/js/vendor/bootstrap_config.json` file.

1. Go to https://getbootstrap.com/docs/3.4/customize/

2. Toggle off all of the checkboxes.

3. Under the "jQuery plugins" section check the boxes next to these plugins:

   - Linked to components
     - Alert dismissal
     - Dropdowns
     - Tooltips
     - Popovers
     - Togglable tabs
   - Magic
     - Collapse

4. Scroll to the bottom of the page and click the "Compile and Download" button.

5. Copy the two .js files into `assets/js/vendor/`, replacing the existing files.

## Wikipedia content

To fetch content for all Encyclopedia Topics which have matching Wikipedia
pages, run this:

    ./manage.py fetch_wikipedia --all --verbosity=2

It might take some time. See `encyclopedia/management/commands/fetch_wikipedia.py` for more options.

## Media files

Whether in local dev or Heroku, we need an S3 bucket to store Media files in (Static files are served using Whitenoise).

1. Go to the IAM service, Users, and 'Add User'.

2. Enter a name and check 'Programmatic access'.

3. 'Attach existing policies directly', and select 'AmazonS3FullAccess'.

4. Create user.

5. Save the Access key and Secret key.

6. On the list of Users, click the user you just made and note the User ARN.

7. Go to the S3 service and 'Create Bucket'. Name it, select the region, and click through to create the bucket.

8. Click the bucket just created and then the 'Permissions' tab. Add this policy, replacing `BUCKET-NAME` and `USER-ARN` with yours:

```json
{
  "Statement": [
    {
      "Sid": "PublicReadForGetBucketObjects",
      "Effect": "Allow",
      "Principal": {
        "AWS": "*"
      },
      "Action": ["s3:GetObject"],
      "Resource": ["arn:aws:s3:::BUCKET-NAME/*"]
    },
    {
      "Action": "s3:*",
      "Effect": "Allow",
      "Resource": ["arn:aws:s3:::BUCKET-NAME", "arn:aws:s3:::BUCKET-NAME/*"],
      "Principal": {
        "AWS": ["USER-ARN"]
      }
    }
  ]
}
```

9. Click on 'CORS configuration' and add this:

```xml
<CORSConfiguration>
<CORSRule>
    <AllowedOrigin>*</AllowedOrigin>
    <AllowedMethod>GET</AllowedMethod>
    <MaxAgeSeconds>3000</MaxAgeSeconds>
    <AllowedHeader>Authorization</AllowedHeader>
</CORSRule>
</CORSConfiguration>
```

10. Upload all the files to the bucket in the required location.

11. Update the server's environment variables for `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY` and `AWS_STORAGE_BUCKET_NAME`.
