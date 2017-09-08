#!/bin/bash


VENV_NAME=$1;
RUN_MIGRATIONS=$2;


echo "=== Begin Vagrant Provisioning using 'config/vagrant/django_setup.sh'"

# Ensure the virtualenv settings in .profile are loaded:
source /home/vagrant/.profile

workon $VENV_NAME

if [[ -f /vagrant/manage.py ]]; then

    if [ $RUN_MIGRATIONS = 'true' ]; then
        echo "Running Django migrations."
        su - vagrant -c "source /home/vagrant/.virtualenvs/$VENV_NAME/bin/activate && cd /vagrant && ./manage.py migrate"
    else
        echo "Not running Django migrations."
    fi

    su - vagrant -c "source /home/vagrant/.virtualenvs/$VENV_NAME/bin/activate && cd /vagrant && ./manage.py collectstatic --noinput"

fi

echo "=== End Vagrant Provisioning using 'config/vagrant/django_setup.sh'"


