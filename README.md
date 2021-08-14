pepysdiary
==========

[![Build Status](https://github.com/philgyford/pepysdiary/workflows/CI/badge.svg)](https://github.com/philgyford/pepysdiary/actions?query=workflow%3ACI)
[![Coverage Status](https://coveralls.io/repos/github/philgyford/pepysdiary/badge.svg?branch=main)](https://coveralls.io/github/philgyford/pepysdiary?branch=main)


This code is used for [www.pepysdiary.com](http://www.pepysdiary.com/). This repository includes fixtures for all of the site's data (apart from user accounts and user-contributed comments) although it's often out of date compared to what's live.

Pushing to `main` will run the commit through [this GitHub Action](https://github.com/philgyford/pepysdiary/actions/workflows/main.yml) to run tests. If it passes, it will be deployed automatically to Heroku.


## Local development setup

We use Docker for local development only, not for the live site.


### 1. Create a .env file

Create a `.env` file containing the below (see the Heroku Setup section for
more details about the variables):

    export AKISMET_API_KEY='YOUR-KEY'

    export ALLOWED_HOSTS='*'

    export AWS_ACCESS_KEY_ID='YOUR-ACCESS-KEY'
    export AWS_SECRET_ACCESS_KEY='YOUR-SECRET-ACCESS-KEY'
    export AWS_STORAGE_BUCKET_NAME='your-bucket-name'

    export DJANGO_SECRET_KEY='YOUR-SECRET-KEY'
    export DJANGO_SETTINGS_MODULE='config.settings.development'

    # For use in Django:
    export DATABASE_URL='postgres://pepysdiary:pepysdiary@pepys_db:5432/pepysdiary'
    # For use in Docker:
    POSTGRES_USER=pepysdiary
    POSTGRES_PASSWORD=pepysdiary
    POSTGRES_DB=pepysdiary

    export MAPBOX_ACCESS_TOKEN='YOUR-ACCESS-TOKEN'
    export MAPBOX_MAP_ID='mapbox/light-v10'

    export RECAPTCHA_PRIVATE_KEY='YOUR-PRIVATE-KEY'
    export RECAPTCHA_PUBLIC_KEY='YOUR-PUBLIC-KEY'

    export SENDGRID_USERNAME='apikey'
    export SENDGRID_PASSWORD=''YOUR_PASSWORD'

    # TBD what this should be when using Docker:
    export REDIS_URL='redis://127.0.0.1:6379/1'


### 2. Set up a local domain name

Open your `/etc/hosts` file in a terminal window by doing:

    $ sudo vim /etc/hosts

Enter your computer's password. Then add this line somewhere in the file and save:

    127.0.0.1 www.pepysdiary.test


### 3. Build the Docker containers

Download, install and run Docker Desktop.

In same directory as this README, build the containers:

    $ docker-compose build

Then start up the web and database containers:

    $ docker-compose up

There are two containers, the webserver (`web`) and the postgres serer (`db`).
All the repository's code is mirrored in the web container in the `/code/` directory.


### 4. Set up the database

Once that's running, showing its logs, open another terminal window/tab.

There are two ways we can populate the database. First we'll create an empty one,
and second we'll populate it with a dump of data from the live site.

#### 4a. An empty database

The `build` step will create the database and run the Django migrations.

Then create a superuser:

    $ ./scripts/manage.sh createsuperuser

(NOTE: The `manage.sh` script is a shortcut for a longer command that runs
Django's `manage.py` within the Docker web container.)

#### 4b. Use a dump from the live site

Log into postgres and drop the current (empty) database:

    $ docker exec -it pepys_db psql -U pepysdiary -d pepysdiary
    # drop database pepysdiary with (FORCE);
	# create database pepysdiary;
	# grant all privileges on database "pepysdiary" to pepysdiary;
    # \q

On Heroku, download a backup file of the live site's database and rename it to
something simpler. We'll use "heroku_db_dump" below.

Put the file in the same directory as this README.

Import the data into the database:

    $ docker exec -i db pepys_pg_restore --verbose --clean --no-acl --no-owner -U pepysdiary -d pepysdiary < heroku_db_dump


#### 5. Vist and set up the site

Then go to http://www.pepysdiary.test:8000 and you should see the site.

Log in to the [Django Admin](http://www.pepysdiary.test:8000/backstage/), go to the "Sites"
section and change the one Site's Domain Name to `www.pepysdiary.test:8000` and the
Display Name to "The Diary of Samuel Pepys".


## Ongoing work

Whenever you come back to start work you need to start the containers up again:

    $ docker-compose up

When you want to stop the server, in the terminal window/tab that's showing the logs, hit `Control` and `X` together.

You can check if anything's running by doing this, which will list any Docker processes:

    $ docker ps

Do this in the project's directory to stop containers:

    $ docker-compose stop

You can also open the Docker Desktop app to see a prettier view of what containers you have.

When the containers are running you can open a shell to the web server (exit with `Control` and `D` together):

    $ docker exec -it pepys_web sh

You could then run `.manage.py` commands within there:

    $ ./manage.py help

Or, use the shortcut command from *outside* of the Docker container:

    $ ./scripts/manage.sh help

Or you can log into the database:

    $ docker exec -it pepys_db psql -U pepysdiary -d pepysdiary

The development environment has [django-extensions](https://django-extensions.readthedocs.io/en/latest/index.html) installed so you can use its `shell_plus` and other commands. e.g.:

    $ ./scripts/manage.sh shell_plus
    $ ./scripts/manage.sh show_urls

To install new python dependencies:

    $ docker exec -it pepys_web sh
    # pipenv install module-name


### Other local dev tasks

#### Editing CSS and JS

We use [Gulp](http://gulpjs.com/) to:

	* Compile the SCSS files into CSS.
	* Minify our custom JavaScript.
	* Concatenate a few JavaScript files into one.
	* Inject paths for these combined files into a Django template or two.

Run this to watch for any changes to the SCSS or JS files:

	$ gulp watch

Or, for a one-off run:

	$ gulp


#### Tests

There are only a handful of tests, but run them with:

	$ ./scripts/run_tests.sh

It will generate HTML coverage reports. View `htmlcov/index.html` in a browser.


## Heroku set-up

For hosting on Heroku, we use these add-ons:

	* Heroku Postgres
	* Heroku Redis (for caching)
	* Heroku Scheduler
	* Papertrail (for viewing/filtering logs)
	* Sentry (for error reporting)

To clear the Redis cache, use our `clear_cache` management command:

	$ heroku run python ./manage.py clear_cache

Note that by default Heroku's Redis is set up with a `maxmemory-policy` of `noeviction` which will generate OOM (Out Of Memory) errors when the memory limit is reached. This [can be changed](https://devcenter.heroku.com/articles/heroku-redis#maxmemory-policy):

    $ heroku redis:info
    === redis-fishery-12345 (HEROKU_REDIS_NAVY_TLS_URL, ...    

Then use that Redis name like:

    $ heroku redis:maxmemory redis-fisher-12345 --policy volatile-lru


## Environment variables

The environment variables the site uses are below. For the local pipenv
environment they're stored in the `.env` file and loaded by pipenv. For Heroku
these are environment settings.

	AKISMET_API_KEY
	ALLOWED_HOSTS
    DATABASE_URL
	DJANGO_SETTINGS_MODULE
    MAPBOX_ACCESS_TOKEN
    MAPBOX_MAP_ID  # e.g. "mapbox/light-v10"
	RECAPTCHA_PRIVATE_KEY
	RECAPTCHA_PUBLIC_KEY
	REDIS_URL
	SENDGRID_USERNAME
	SENDGRID_PASSWORD

`REDIS_URL` is used on prodution and _can be_ used on development, if there's
a redis server running and we set the `CACHES` setting to use it in
`config/settings/development.py`.


## Bootstrap

W're using Boostrap SASS to generate a custom set of Bootstrap CSS. Comment/uncomment lines in `pepysdiary/common/static/src/sass/_bootstrap_custom.scss` to change whichparts of Bootstrap's CSS are included in the generated CSS file.

### Bootstrap's JavaScript

We must manually download a custom version of Bootstrap's JavaScript file.

Instead of steps 2 and 3 you can hopefully upload the `js/src/vendor/bootstrap_config.json` file.

1. Go to http://getbootstrap.com/customize/
2. Toggle off all of the checkboxes.
3. Under the "jQuery plugins" section check the boxes next to these plugins:

	* Linked to components
		* Alert dismissal
		* Dropdowns
		* Tooltips
		* Popovers
		* Togglable tabs
	* Magic
		* Collapse

4. Scroll to the bottom of the page and click the "Compile and Download" button.
5. Copy the two .js files into `pepysdiary/common/static/js/libs/`, replacing the existing files.


## Wikipedia content

To fetch content for all Encyclopedia Topics which have matching Wikipedia
pages, run:

	$ ./manage.py fetch_wikipedia --all --verbosity=2

It might take some time. See `encyclopedia/management/commands/fetch_wikipedia.py` for more options.


## Other notes

Lots of site-wide stuff is in the `pepysdiary/common/` app. Including the CSS, JS and images in `pepysdiary/common/static/`.
