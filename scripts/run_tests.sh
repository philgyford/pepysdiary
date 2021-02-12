#!/bin/bash
set -e

# Call this from the host machine.
# It will call the `tests` shortcut defined in Pipfile, which will run
# a script within the pipenv environment.

# You can optionally pass in a test, or test module or class, as an argument.
# e.g.
# ./run_tests.sh tests.appname.test_models.TestClass.test_a_thing
TESTS_TO_RUN=${1:tests}

docker exec pepys_web /bin/sh -c "pipenv run manage.py test --settings=pepysdiary.settings.tests $TESTS_TO_RUN ; pipenv run flake8"