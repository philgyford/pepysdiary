pepysdiary
==========

This code is used for [www.pepysdiary.com](http://www.pepysdiary.com/). This repository includes fixtures for all of the site's data (apart from user accounts and user-contributed comments) although it's often out of date compared to what's live.

I don't expect anyone else will want to run this, so there's no in-depth installation guide.

Requires Django 1.6.1.

If you want to run it locally, then copy `pepysdiary/settings/development_template.py` to `pepysdiary/settings/development.py` and set things accordingly. Then do:

	$ ./manage.py runserver

To run on Heroku you'll need to set all the environment variables required in `pepysdiary/settings/heroku.py`.

But first run this to transfer all static elements to S3:

	$ heroku run ./manage.py collectstatic --settings=pepysdiary.settings.heroku

## Compass, SASS, CSS

This uses [Compass](http://compass-style.org/) to generate CSS files from the [SASS](http://sass-lang.com/) files in `pepysdiary/common/static/sass/`. Compass is Ruby.

From the top-level directory of this project, run:

	$ bundle install

to install the gems specified in `Gemfile` (Compass and [Bootstrap Sass](https://github.com/twbs/bootstrap-sass/)).

Then, run this:

	$ compass watch .

to have Compass continually watch the SASS files for any changes, and compile a new `pepysdiary/common/static/css/pepysdiary.css` file.

We don't do any clever deploy stuff to compile the SASS files; it's all done before commiting the changes to this repository.

## Bootstrap

As mentioned above, we're using Boostrap SASS to generate a custom set of Bootstrap CSS. Comment/uncomment lines in `pepysdiary/common/static/sass/_bootstrap_custom.scss` to change which parts of Bootstrap's CSS are included in teh generated CSS file.

For a custom version of Bootstrap's JavaScript file, we have to use http://getbootstrap.com/customize/ to generate it. Under the "jQuery plugins" section, we currently have these checked before downloading the JS file:

	* Linked to components
		* Dropdowns
		* Tooltips
		* Popovers
	* Magic
		* Collapse

## Other notes

Lots of site-wide stuff is in the `pepysdiary/common/` app. Including the CSS, JS and images in `pepysdiary/common/static/`.
