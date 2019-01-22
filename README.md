pepysdiary
==========

This code is used for [www.pepysdiary.com](http://www.pepysdiary.com/). This repository includes fixtures for all of the site's data (apart from user accounts and user-contributed comments) although it's often out of date compared to what's live.

Uses Python 3.6.x and Django 1.9.x.


## Local development

### Setup

Install python requirements:

	$ pipenv install --dev

In the Django Admin set the Domain Name of the one Site.

Create a database user with the required privileges:

	$ psql
	# create database pepysdiary;
	# create user pepysdiary with password 'pepysdiary';
	# grant all privileges on database "django-hines" to hines;
	# alter user pepysdiary createdb;

I got an error ("permission denied for relation django_migrations") later:

	$ psql "pepysdiary" -c "GRANT ALL ON ALL TABLES IN SCHEMA public to pepysdiary;"
	$ psql "pepysdiary" -c "GRANT ALL ON ALL SEQUENCES IN SCHEMA public to pepysdiary;"
	$ psql "pepysdiary" -c "GRANT ALL ON ALL FUNCTIONS IN SCHEMA public to pepysdiary;"

Probably need to do this for a fresh install:

	$ pipenv shell
	$ ./manage.py migrate
	$ ./manage.py collectstatic
	$ ./manage.py createsuperuser

*OR*, download the database backup file from Heroku and do this:

	$ pg_restore -d pepysdiary my_dump_file

Then run the webserver:

	$ pipenv run ./manage.py runserver

Then visit http://localhost:8000 or http://127.0.0.1:8000.

In the Django Admin set the Domain Name of the one Site.


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

	$ ./manage.py test


## Environment variables

The environment variables the site uses are below. For the local pipenv
environment they're stored in the `.env` file and loaded by pipenv. For Heroku
these are environment settings.

	AKISMET_API_KEY
	ALLOWED_HOSTS
	DB_NAME
	DB_USERNAME
	DB_HOST
	DB_PASSWORD
	DJANGO_SETTINGS_MODULE
	MAPBOX_ACCESS_TOKEN
	MAPBOX_ACCESS_ID
	RECAPTCHA_PRIVATE_KEY
	RECAPTCHA_PUBLIC_KEY
	SENDGRID_USERNAME
	SENDGRID_PASSWORD


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
