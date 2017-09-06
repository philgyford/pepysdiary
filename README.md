pepysdiary
==========

This code is used for [www.pepysdiary.com](http://www.pepysdiary.com/).

Uses Python 2.7.x and Django 1.11.x.


## Local development using Vagrant

There is a Vagrantfile, and accompanying config and shell scripts in `config/`,
based on [this repo](https://github.com/philgyford/vagrant-heroku-cedar-16-python). With a following wind you should be able to do:

    $ vagrant up

To get a version of the site up and running and accessible at
http://0.0.0.0:5000. Apart from no data in the database (see that Vagrant repo
for import instructions), and no "media" files (see below).

Log in to admin and change the Site domain name.

### Front-end building

We use gulp to build the front-end CSS and JS files. The minified files are
committed to git. The `base.html` template is updated with references to the
created files, with unique names.

#### Installation

Install all the requirements...

The usual node via apt-get is rather behind, so we use a different source:

    $ vagrant ssh
    vagrant$ curl -sL https://deb.nodesource.com/setup_6.x | sudo -E bash -
    vagrant$ sudo apt-get install -y nodejs

And we want `node` to work, but by default on ubuntu it's only `nodejs`. So:

    vagrant$ sudo ln -s /usr/bin/nodejs /usr/bin/node

Then add npm and gulp:

    vagrant$ sudo apt-get install npm
    vagrant$ sudo npm install -g gulp-cli

Install required node modules from `package.json`:

    vagrant$ cd /vagrant
    vagrant$ npm install

#### Usage

    $ vagrant ssh
    vagrant$ cd /vagrant

Then, this will recreate all the CSS and JS files:

    vagrant$ gulp

To watch for changes in any of the files:

    vagrant$ gulp watch

The latter won't notice changes in any JS files in `static/src/js/vendor/`.

Links to CSS and JS files in `templates/500.html` won't currently be changed
automatically.


## Heroku site

To set up a new copy of the site on Heroku.

1. Create an S3 bucket for Media files (see below) and copy them there.

2. Create a new Heroku app and add it as a git remote.

3. Add a Heroku Postgres add-on.

4. Add the Memcachier (Free) add-on.

6. Add the Heroku Scheduler (Free) add-on.

7. Set all environment variables with `heroku config:set`.

8. Push code to Heroku: `git push heroku master`.

9. Set the Heroku dyno to be Hobby Basic, if necessary.

10. Upload a postgres backup file somewhere with an accessible URL.

11. Import postgres data using `heroku pg:backups:restore
   'http://your-url-here'`.

12. Delete the postgres backup file you uploaded somewhere.

13. Log in to Django admin and change the Site domain name (if necessary).

14. Go to the Heroku Scheduler Resource and add a new Job to run once a day:

    ```
    python manage.py fetch_wikipedia --num=100
    ```

## Environment variables

The environment variables the site uses:

	AKISMET_API_KEY
	ALLOWED_HOSTS
    AWS_ACCESS_KEY_ID
    AWS_SECRET_ACCESS_KEY
    AWS_STORAGE_BUCKET_NAME
	DJANGO_SETTINGS_MODULE
	MAPBOX_ACCESS_TOKEN
	MAPBOX_MAP_ID
	RECAPTCHA_PRIVATE_KEY
	RECAPTCHA_PUBLIC_KEY
    SECRET_KEY
	SENDGRID_USERNAME
	SENDGRID_PASSWORD

### Additional Vagrant-only env vars

	DB_NAME
	DB_USERNAME
	DB_HOST
	DB_PASSWORD

### Additional Heroku-only env vars

Created automatically by add-ons:

    DATABASE_URL
    MEMCACHIER_PASSWORD
    MEMCACHIER_SERVERS
    MEMCACHIER_USERNAME


## Media files

Whether using Vagrant or Heroku, we need an S3 bucket to store Media files in
(Static files are served using Whitenoise).

1. Go to the IAM service, Users, and 'Add User'.

2. Enter a name and check 'Programmatic access'.

3. 'Attach existing policies directly', and select 'AmazonS3FullAccess'.

4. Create user.

5. Save the Access key and Secret key.

6. On the list of Users, click the user you just made and note the User ARN.

7. Go to the S3 service and 'Create Bucket'. Name it, select the region, and click through to create the bucket.

8. Click the bucket just created and then the 'Permissions' tab. Add this
   policy, replacing `BUCKET-NAME` and `USER-ARN` with yours:

    ```
    {
        "Statement": [
            {
              "Sid":"PublicReadForGetBucketObjects",
              "Effect":"Allow",
              "Principal": {
                    "AWS": "*"
                 },
              "Action":["s3:GetObject"],
              "Resource":["arn:aws:s3:::BUCKET-NAME/*"
              ]
            },
            {
                "Action": "s3:*",
                "Effect": "Allow",
                "Resource": [
                    "arn:aws:s3:::BUCKET-NAME",
                    "arn:aws:s3:::BUCKET-NAME/*"
                ],
                "Principal": {
                    "AWS": [
                        "USER-ARN"
                    ]
                }
            }
        ]
    }
    ```

9. Click on 'CORS configuration' and add this:

    ```
    <CORSConfiguration>
        <CORSRule>
            <AllowedOrigin>*</AllowedOrigin>
            <AllowedMethod>GET</AllowedMethod>
            <MaxAgeSeconds>3000</MaxAgeSeconds>
            <AllowedHeader>Authorization</AllowedHeader>
        </CORSRule>
    </CORSConfiguration>
    ```

10. Create a `/media/` directory in the bucket and upload all the files.

11. Update the server's environment variables for `AWS_ACCESS_KEY_ID`,
    `AWS_SECRET_ACCESS_KEY` and `AWS_STORAGE_BUCKET_NAME`.


## Wikipedia content

To fetch content for all Encyclopedia Topics which have matching Wikipedia
pages, run:

	$ ./manage.py fetch_wikipedia --all --verbosity=2

It might take some time. See `encyclopedia/management/commands/fetch_wikipedia.py` for more options.


----
Everything below this line might be way out of date...

## Installation

We're using [this Ansible playbook](https://github.com/philgyford/ansible-playbook).

Add the site as a new app as per the playbook's instructions. Set up the app's variables, download and import the database, manually copy any existing Django media files to the new server.

The environment variables the site uses:

	AKISMET_API_KEY
	ALLOWED_HOSTS
    AWS_ACCESS_KEY_ID
    AWS_SECRET_ACCESS_KEY
    AWS_STORAGE_BUCKET_NAME
	DB_NAME
	DB_USERNAME
	DB_HOST
	DB_PASSWORD
	DJANGO_SETTINGS_MODULE
	MAPBOX_ACCESS_TOKEN
	MAPBOX_ACCESS_ID
	RECAPTCHA_PRIVATE_KEY
	RECAPTCHA_PUBLIC_KEY
    SECRET_KEY
	SENDGRID_USERNAME
	SENDGRID_PASSWORD


## Development (might be out of date)

Summary:

* `cd django-pepysdiary`
* Install the Ruby SASS gem (`bundle install --path vendor/bundle`)
* Install Node.js and NPM.
* Install Gulp (`npm install`).
* Watch for changes to SCSS and JS files with `npm run watch`.

More detail:

### SASS and CSS

This uses [SASS](http://sass-lang.com/), generating CSS files from the SCSS in `pepysdiary/common/static/sass/`. Compass is Ruby. Settings for this are in `config.rb`.

To ensure SASS (Ruby) is installed, rom the top-level directory of this project, run:

	$ bundle install --path vendor/bundle

to install the gem specified in `Gemfile` (SASS) and install it locally.

To update all the gems to the latest versions:

	$ bundle update


### Gulp

We use [Gulp](http://gulpjs.com/) to:

	* Compile the SCSS files into CSS.
	* Minify our custom JavaScript.
	* Concatenate a few JavaScript files into one.

You'll need [Node.js](http://nodejs.org/) and [Node Package Manager](https://www.npmjs.org/). Once those are installed, then running this from inside the same directory as `package.json` should install the required Node packages for Gulp:

	$ npm install

Then run this to watch for any changes to the SCSS or JS files:

	$ npm run watch

Or, for a one-off run:

	$ npm run gulp


## Bootstrap

As mentioned above, we're using Boostrap SASS to generate a custom set of Bootstrap CSS. Comment/uncomment lines in `pepysdiary/common/static/sass/_bootstrap_custom.scss` to change which parts of Bootstrap's CSS are included in the generated CSS file.

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


## Setting up with Ansible

Using https://github.com/philgyford/ansible-playbook on DigitalOcean.

1. Follow the DigitalOcean instructions in that README.

2. Maybe: Follow the "Django database" section, to destro empty database and import from a backup.

3. Maybe: Upload Media files.

