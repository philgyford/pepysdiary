# pepysdiary

[![Build Status](https://github.com/philgyford/pepysdiary/workflows/CI/badge.svg)](https://github.com/philgyford/pepysdiary/actions?query=workflow%3ACI)
[![codecov](https://codecov.io/gh/philgyford/pepysdiary/branch/main/graph/badge.svg?token=GD97K3Q26Z)](https://codecov.io/gh/philgyford/pepysdiary)
[![Code style: prettier](https://img.shields.io/badge/code_style-prettier-ff69b4.svg?style=flat-square)](https://github.com/prettier/prettier)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)

Code for [www.pepysdiary.com](http://www.pepysdiary.com/).

Pushing to `main` will run the commit through [this GitHub Action](https://github.com/philgyford/pepysdiary/actions/workflows/main.yml) to run tests. If it passes, it will be deployed automatically to the website.

When changing the python version, it will need to be changed in:

- `.github/workflows/main.yml`
- `.pre-commit-config.yaml`
- `.python-version` (for pyenv)
- `runtime.txt` (for Heroku)
- `pyproject.toml` (black's target-version)
- `Dockerfile`

For local development we use Docker. The live site is on an Ubuntu 22 VPS.

## Local development setup

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

    $ docker-compose build

Then start up the web, assets and database containers:

    $ docker-compose up

There are four containers:

- `pepysdiary_web`: the webserver
- `pepysdiary_db`: the postgres server
- `pepysdiary_assets`: the front-end assets builder
- `pepysdiary_redis`: the redis server (for optional caching)

All the repository's code is mirrored in the web and assets containers in the `/code/` directory.

### 4. Set up the database

Once that's running, showing the logs, open another terminal window/tab.

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

On the VPS, create a backup file of the live site's database:

    $ pg_dump dbname -U username -h localhost | gzip > ~/pepys_dump.gz

Then scp it to your local machine:

    $ scp username@your.vps.domain.com:/home/username/pepys_dump.gz .

Put the file in the same directory as this README.

Import the data into the database ():

    $ gunzip pepys_dump.gz
    $ docker exec -i pepys_db pg_restore --verbose --clean --no-acl --no-owner -U pepysdiary -d pepysdiary < pepys_dump

#### 5. Vist and set up the site

Then go to http://www.pepysdiary.test:8000 and you should see the site.

Log in to the [Django Admin](http://www.pepysdiary.test:8000/backstage/), go to the "Sites" section and change the one Site's Domain Name to `www.pepysdiary.test:8000` and the Display Name to "The Diary of Samuel Pepys", if it's not already.

## Ongoing work

### Docker

Whenever you come back to start work you need to start the containers up again by doing this from the project directory:

    $ docker-compose up

When you want to stop the server, then this from the same directory:

    $ docker-compose down

You can check if anything's running by doing this, which will list any Docker processes:

    $ docker ps

See details on the `./run` script below for running things inside the containers.

### Python dependencies with virtualenv and pip-tools

Adding and removing python depenencies is most easily done with a virtual environment on your host machine. This also means you can use that environment easily in VS Code.

Set up and activate a virtual environment on your host machine using [virtualenv](https://virtualenv.pypa.io/en/latest/):

    $ virtualenv --prompt . venv
    $ source venv/bin/activate

We use [pip-tools](https://pip-tools.readthedocs.io/en/latest/) to generate `requirements.txt` from `requirements.in`, and install the dependencies. Install the current dependencies into the activated virtual environment:

    (venv) $ python -m pip install -r requirements.txt

To add a new depenency, add it to `requirements.in` and then regenerate `requirements.txt`:

    (venv) $ pip-compile --upgrade --quiet --generate-hashes

And do the `pip install` step again to install.

To remove a dependency, delete it from `requirements.in`, run that same `pip-compile` command, and then:

    (venv) $ python -m pip uninstall <module-name>

To update the python dependencies in the Docker container, this should work:

    $ ./run pipsync

But you might have to do `docker-compose build` instead?

### pre-commit

Install [pre-commit](https://pre-commit.com) to run `.pre-commit-config.yml` automatically when `git commit` is done.

## Front-end assets

Gulp is used to build the final CSS and JS file(s), and watches for changes in the `pepysdiary_assets` container. Node packages are installed and upgraded using `yarn` (see `./run` below).

## The ./run script

The `./run` script makes it easier to run things that are within the Docker containers. This will list the commands available, which are outlined below:

    $ ./run

### `./run cmd`

Run any command in the web container. e.g.

    $ ./run cmd ls -al

### `./run sh`

Starts a Shell session in the web container.

### `./run manage`

Run the Django `manage.py` file with any of the usual commands, within the pipenv virtual environment. e.g.

    $ ./run manage makemigrations

The development environment has [django-extensions](https://django-extensions.readthedocs.io/en/latest/index.html) installed so you can use its `shell_plus` and other commands. e.g.:

    $ ./run manage shell_plus
    $ ./run manage show_urls

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

### `./run pipsync`

Update the installed python depenencies depending on the contents of `requirements.txt`.

### `./run yarn:outdated`

List any installed Node packages (used for building front end assets) that are outdated.

### `./run yarn:upgrade`

Update any installed Node packages that are outdated.

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
