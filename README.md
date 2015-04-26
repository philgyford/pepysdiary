pepysdiary
==========

This code is used for [www.pepysdiary.com](http://www.pepysdiary.com/). This repository includes fixtures for all of the site's data (apart from user accounts and user-contributed comments) although it's often out of date compared to what's live.

I don't expect anyone else will want to run this, so there's no in-depth installation guide.

Requires Django 1.7.x.

Can be run in Vagrant using https://github.com/philgyford/vagrant-heroku-cedar-14-python (symlink that projects `Vagrantfile` and `config/vagrant/` into the root of `django-pepysdiary/`).

If you want to run it locally, then copy `pepysdiary/settings/development_template.py` to `pepysdiary/settings/development.py` and set things accordingly. Then do:

	$ ./manage.py runserver

To run on Heroku you'll need to set all the environment variables required in `pepysdiary/settings/heroku.py`.

And also specify that settings file itself by setting the `DJANGO_SETTINGS_MODULE` environment variable. ie:

	$ heroku config:set DJANGO_SETTINGS_MODULE=pepysdiary.settings.heroku

But first run this to transfer all static elements to S3. (Note, this seems to happen automatically when pushing to Heroku these days.):

	$ heroku run ./manage.py collectstatic --app=pepysdiary --settings=pepysdiary.settings.heroku

(The `--app` setting only needed if you have more than one set up, eg `pepysdiary-staging` too.)


## Development

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
