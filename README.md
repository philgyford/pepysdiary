# pepysdiary

[![Build Status](https://github.com/philgyford/pepysdiary/workflows/CI/badge.svg)](https://github.com/philgyford/pepysdiary/actions?query=workflow%3ACI)
[![Coverage Status](https://coveralls.io/repos/github/philgyford/pepysdiary/badge.svg?branch=main)](https://coveralls.io/github/philgyford/pepysdiary?branch=main)
[![Code style: prettier](https://img.shields.io/badge/code_style-prettier-ff69b4.svg?style=flat-square)](https://github.com/prettier/prettier)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Code for [www.pepysdiary.com](http://www.pepysdiary.com/). This repository includes fixtures for all of the site's data (apart from user accounts and user-contributed comments) although it's out of date compared to what's live.

Pushing to `main` will run the commit through [this GitHub Action](https://github.com/philgyford/pepysdiary/actions/workflows/main.yml) to run tests. If it passes, it will be deployed automatically to Heroku.

## Local development setup

### 1. Create a .env file

Create a `.env` file containing the below (see the Custom Django Settings section below for more about some of the variables):

    export AKISMET_API_KEY='YOUR-API-KEY'

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
    export SENDGRID_PASSWORD='YOUR_PASSWORD'

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

Then start up the web, assets and database containers:

    $ docker-compose up

There are three containers, the webserver (`pepysdiary_web`), the front-end assets builder (`pepysdiary_assets`) and the postgres server (`pepysdiary_db`). All the repository's code is mirrored in the web container in the `/code/` directory.

### 4. Set up the database

Once that's running, showing its logs, open another terminal window/tab.

There are two ways we can populate the database. First we'll create an empty one, and second we'll populate it with a dump of data from the live site.

#### 4a. An empty database

The `build` step will create the database and run the initial Django migrations.

Then create a superuser:

    $ ./run manage createsuperuser

(See below for more info on the `./run` script.)

#### 4b. Use a dump from the live site

Log into postgres and drop the current (empty) database:

    $ ./run psql -d postgres
    # drop database pepysdiary with (FORCE);
    # create database pepysdiary;
    # grant all privileges on database pepysdiary to pepysdiary;
    # \q

On Heroku, download a backup file of the live site's database and rename it to something simpler. We'll use "heroku_db_dump" below.

Put the file in the same directory as this README.

Import the data into the database ():

    $ docker exec -i pepysdiary_db pg_restore --verbose --clean --no-acl --no-owner -U pepysdiary -d pepysdiary < heroku_db_dump

#### 5. Vist and set up the site

Then go to http://www.pepysdiary.test:8000 and you should see the site.

Log in to the [Django Admin](http://www.pepysdiary.test:8000/backstage/), go to the "Sites" section and change the one Site's Domain Name to `www.pepysdiary.test:8000` and the Display Name to "The Diary of Samuel Pepys", if it's not already.

## Ongoing work

Whenever you come back to start work you need to start the containers up again by doing this from the project directory:

    $ docker-compose up

When you want to stop the server, then this from the same directory:

    $ docker-compose down

You can check if anything's running by doing this, which will list any Docker processes:

    $ docker ps

See details on the `./run` script below for running things inside the containers.

VS Code will use the python environment on the web Docker container for autocompletion etc.

## Front-end assets

Gulp is used to build the final CSS and JS file(s), and watches for changes in the `pepysdiary_assets` container. Node packages are installed and upgraded using `yarn` (see `./run` below).

## The ./run script

The `./run` script makes it easier to run things that are within the Docker containers. This will list the commands available, which are outlined below:

    ./run

### `./run cmd`

Run any command in the web container. e.g.

    ./run cmd ls -al

### `./run sh`

Starts a Shell session in the web container.

### `./run manage`

Run the Django `manage.py` file with any of the usual commands, within the pipenv virtual environment. e.g.

    ./run manage makemigrations

The development environment has [django-extensions](https://django-extensions.readthedocs.io/en/latest/index.html) installed so you can use its `shell_plus` and other commands. e.g.:

    $ ./run manage shell_plus
    $ ./run manage show_urls

### `./run tests`

It runs `collectstatic` and then runs all the Django tests.

Run a folder, file, or class of tests, or a single test, something like this:

    ./run tests tests.core
    ./run tests tests.core.test_views
    ./run tests tests.core.test_views.HomeViewTestCase
    ./run tests tests.core.test_views.HomeViewTestCase.test_response_200

### `./run coverage`

It runs `collectstatic` and then all the tests with coverage. The HTML report files will be at `htmlcov/index.html`.

### `./run flake8`

Lints the python code with flake8. Add any required arguments on the end.

### `./run black`

Runs the Black formatter over the python code. Add any required arguments on the end.

### `./run psql`

Conects to PosgreSQL with psql. Add any required arguments on the end. Uses the `pepysdiary` database unless you specify another like:

    ./run psql -d databasename

### `./run pipenv:outdated`

List any installed python packages (default and develop) that are outdated.

### `./run pipenv:update`

Update any installed python packages (default and develop) that are outdated.

### `./run yarn:outdated`

List any installed Node packages (used for building front end assets) that are outdated.

### `./run yarn:upgrade`

Update any installed Node packages that are outdated.

## Heroku set-up

For hosting on Heroku, we use these add-ons:

- Heroku Postgres
- Heroku Redis (for caching)
- Heroku Scheduler
- Papertrail (for viewing/filtering logs)
- Sentry (for error reporting)

The site will require Config settings to be set-up as in the local development `.env` (above) and see the Django settings (below).

To clear the Redis cache, use our `clear_cache` management command:

    $ heroku run python ./manage.py clear_cache

Note that by default Heroku's Redis is set up with a `maxmemory-policy` of `noeviction` which will generate OOM (Out Of Memory) errors when the memory limit is reached. This [can be changed](https://devcenter.heroku.com/articles/heroku-redis#maxmemory-policy):

    $ heroku redis:info
    === redis-fishery-12345 (HEROKU_REDIS_NAVY_TLS_URL, ...

Then use that Redis name like:

    $ heroku redis:maxmemory redis-fisher-12345 --policy allkeys-lru

### Heroku Config Vars

Set these Config Vars in Heroku (see the Custom Django Settings section below for more about some of the variables):

```
AKISMET_API_KEY             YOUR-API-KEY
ALLOWED_HOSTS               pepysdiary-production.herokuapp.com,www.pepysdiary.com
AWS_ACCESS_KEY_ID           YOUR-ACCESS-KEY
AWS_SECRET_ACCESS_KEY       YOUR-SECRET-ACCESS-KEY
AWS_STORAGE_BUCKET_NAME     your-bucket-nuame
DJANGO_SECRET_KEY           YOUR-SECRET-KEY
DJANGO_SETTINGS_MODULE      pepysdiary.settings.production
MAPBOX_ACCESS_TOKEN         YOUR-ACCESS-TOKEN
MAPBOX_MAP_ID               mapbox/light-v10
RECAPTCHA_PRIVATE_KEY       YOUR-PRIVATE-KEY
RECAPTCHA_PUBLIC_KEY        YOUR-PUBLIC-KEY
SENDGRID_USERNAME           apikey
SENDGRID_PASSWORD           YOUR_PASSWORD
WEB_CONCURRENCY             2
```

Further settings will be set automatically by add-ons.

## Custom Django Settings

Custom settings that can be in the Django `settings.py` file:

`AKISMET_API_KEY`: To enable checking submitted comments for spam using [Akismet](https://akismet.com) set this to your API key, a string. If `None` then no spam checking is done using Akismet. `None` is the default. By default this is picked up from a `AKISMET_API_KEY` environment variable.

`GOOGLE_ANALYTICS_ID` for Google Analytics.

`MAPBOX_ACCESS_TOKEN`: To access the mapbox.com API

`MAPBOX_MAP_ID` e.g. "mapbox/light-v10"

`RECAPTCHA_PRIVATE_KEY` and `RECAPTCHA_PUBLIC_KEY`: To activate the Recaptcha on the sign-up form.

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
