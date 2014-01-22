pepysdiary
==========

This code is used for [www.pepysdiary.com](http://www.pepysdiary.com/). This repository includes fixtures for all of the site's data (apart from user accounts and user-contributed comments) although it's often out of date compared to what's live.

I don't expect anyone else will want to run this, so there's no in-depth installation guide.

Requires Django 1.5.x.

If you want to run it locally, then copy `pepysdiary/settings/development_template.py` to `pepysdiary/settings/development.py` and set things accordingly. Then do:

	$ ./manage.py runserver

To run on Heroku you'll need to set all the environment variables required in `pepysdiary/settings/heroku.py`.

But first run this to transfer all static elements to S3:

$ heroku run ./manage.py collectstatic --settings=pepysdiary.settings.heroku

