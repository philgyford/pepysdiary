#!/bin/bash
set -e

# Call this from the host machine.
# It will call the `tests` shortcut defined in Pipfile, which will run
# a script within the pipenv environment. Flake8 and Coverage will also be run.

# You can optionally pass in a test, or test module or class, as an argument.
# e.g.
# ./run_tests.sh tests.appname.test_models.TestClass.test_a_thing
# In this case Flake8 and Coverage will NOT be run.
TESTS_TO_RUN=${1:tests}

if [[ $TESTS_TO_RUN == "tests" ]]
then
    # Coverage config is in setup.cfg
    docker exec pepys_web /bin/sh -c "pipenv run coverage run manage.py test --settings=pepysdiary.settings.tests $TESTS_TO_RUN ; pipenv run flake8; pipenv run coverage html"
else
    docker exec pepys_web /bin/sh -c "pipenv run python manage.py test --settings=pepysdiary.settings.tests $TESTS_TO_RUN"
fi
