#!/bin/bash

# Install and (if there's a Procfile) start foreman.
# Needs to come after the virtualenv has been set up.

# Expects three arguments:
VIRTUALENV_NAME=$1
DJANGO_SETTINGS_MODULE=$2
PROCFILE=$3
START_FOREMAN=$4

echo "=== Begin Vagrant Provisioning using 'config/vagrant/foreman_setup.sh'"

if [ -z `which foreman` ]; then
    gem install foreman --no-ri --no-rdoc
fi

if ! grep -Fq "DJANGO_SETTINGS_MODULE" /home/vagrant/.bashrc; then
    echo "export DJANGO_SETTINGS_MODULE=${DJANGO_SETTINGS_MODULE}" >> /home/vagrant/.bashrc
fi


if [[ -f /vagrant/$PROCFILE ]]; then
    if [ $START_FOREMAN ]; then
        echo "Procfile found (${PROCFILE}); starting foreman."

        export DJANGO_SETTINGS_MODULE="$DJANGO_SETTINGS_MODULE"

        # Ensure the virtualenv settings in .profile are loaded:
        source /home/vagrant/.profile

        # Run with & to release the terminal.
        # Although that may also rely on the Procfile's processes having their
        # output sent to a file, not stdout/stderr.
        foreman start -f /vagrant/$PROCFILE &
    else
        echo "Not starting foreman."
    fi
else
    echo "No Procfile found; not starting foreman."
fi

echo "=== End Vagrant Provisioning using 'config/vagrant/foreman_setup.sh'"

