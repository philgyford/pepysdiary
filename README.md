pepysdiary
==========

This code is used for [www.pepysdiary.com](http://www.pepysdiary.com/). This repository includes fixtures for all of the site's data (apart from user accounts and user-contributed comments) although it's often out of date compared to what's live.

Uses Python 3.6.x and Django 1.9.x.


## Local development

### Setup

We're using [this Vagrant setup](https://github.com/philgyford/vagrant-heroku-cedar-16-python). Media files are stored in an S3 bucket.

	$ vagrant up

Once done, then, for a fresh install:

	$ vagrant ssh
	vagrant$ cd /vagrant
	vagrant$ source .env
	vagrant$ ./manage.py migrate
	vagrant$ ./manage.py collectstatic
	vagrant$ ./manage.py createsuperuser
	vagrant$ ./manage.py runserver 0.0.0.0:5000

Then visit http://localhost:5000 or http://127.0.0.1:5000.

In the Django Admin set the Domain Name of the one Site.

### Ongoing work

Once the Vagrant box is set up then in future do as above, but skip the `migrate` `collectstatic` and `createsuperuser` steps.


### Front end development - setup

Once the Vagrant box is up and running, ssh into it and then install Ruby using
rbenv ([via](https://gorails.com/setup/ubuntu/14.04)):

	$ git clone https://github.com/rbenv/rbenv.git ~/.rbenv
	$ echo 'export PATH="$HOME/.rbenv/bin:$PATH"' >> ~/.bashrc
	$ echo 'eval "$(rbenv init -)"' >> ~/.bashrc
	$ exec $SHELL

	$ git clone https://github.com/rbenv/ruby-build.git ~/.rbenv/plugins/ruby-build
	$ echo 'export PATH="$HOME/.rbenv/plugins/ruby-build/bin:$PATH"' >> ~/.bashrc
	$ exec $SHELL

	$ rbenv install 2.4.0
	$ rbenv global 2.4.0

	$ gem install bundler
	$ rbenv rehash

Then install Sass:

	$ gem install sass

Install Node ([via](https://nodejs.org/en/download/package-manager/)):

	$ curl -sL https://deb.nodesource.com/setup_6.x | sudo -E bash -
	$ sudo apt-get install -y nodejs

Install Gulp etc using npm, as defined in `package.json`:

	$ cd /vagrant
	$ npm install

Install the command line command for gulp:

	$ sudo npm install --global gulp-cli


### Front end development - ongoing

We use [Gulp](http://gulpjs.com/) to:

	* Compile the SCSS files into CSS.
	* Minify our custom JavaScript.
	* Concatenate a few JavaScript files into one.
	* Inject paths for these combined files into a Django template or two.

Run this to watch for any changes to the SCSS or JS files:

	$ gulp watch

Or, for a one-off run:

	$ gulp


## Environment variables

The environment variables the site uses:

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
