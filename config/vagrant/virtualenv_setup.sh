#!/bin/bash

# This will:
# * Install pip, virtualenv and virtualenvwrapper.
# * Set up virtualenvwrapper's paths etc.
# * Create a new virtualenv.
# * Install any pip requirements from the requirements.txt file.

# Expects one argument, the name of the virtualenv.

# The name we'll use for the virtualenv in which we'll install requirements:
VENV_NAME=$1
REQUIREMENTS_FILE=$2

echo "=== Begin Vagrant Provisioning using 'config/vagrant/virtualenv_setup.sh'"

# virtualenv global setup
if ! command -v pip; then
    easy_install -U pip
fi

if [[ ! -f /usr/local/bin/virtualenv ]]; then
    easy_install virtualenv virtualenvwrapper
fi


# If it doesn't look like .bashrc has the required virtualenvwrapper lines in,
# then add them.
if ! grep -Fq "WORKON_HOME" /home/vagrant/.profile; then
    echo "Adding virtualenvwrapper locations to .profile"

    if [[ -d /vagrant/config/virtualenvwrapper/vagrant ]]; then
        echo "Setting the virtualenv to use hooks in /vagrant/config/virtualenvwrapper/vagrant"
        echo "export VIRTUALENVWRAPPER_HOOK_DIR=/vagrant/config/virtualenvwrapper/vagrant" >> /home/vagrant/.profile
    fi

    echo "export WORKON_HOME=/home/vagrant/.virtualenvs" >> /home/vagrant/.profile
    echo "export PROJECT_HOME=/home/vagrant/Devel" >> /home/vagrant/.profile
    echo "source /usr/local/bin/virtualenvwrapper.sh" >> /home/vagrant/.profile
fi

# Get .virtualenvwrapper env variables set up:
source /home/vagrant/.profile

if [[ -d /home/vagrant/.virtualenvs/$VENV_NAME ]]; then
    echo "Activating virtualenv $VENV_NAME."
    workon $VENV_NAME
else
    PYTHON_VERSION='python'

    # If runtime.txt specifies Python 3, use that for the virtualenv:
    if [[ -f /vagrant/runtime.txt ]]; then
        python_runtime=$(head -n 1 /vagrant/runtime.txt)
        if [[ $python_runtime =~ ^python-3\.6 ]]; then
            PYTHON_VERSION='python3.6'
        fi
    fi

    echo "Making new virtualenv $VENV_NAME ($PYTHON_VERSION)."
    # Also switches to the virtualenv:
    mkvirtualenv --python=`which $PYTHON_VERSION` $VENV_NAME

    if [[ -f /vagrant/.env ]]; then
        echo "Linking /vagrant/.env to the virtualenv's postactivate hook"
        rm /home/vagrant/.virtualenvs/pepysdiary/bin/postactivate
        ln -s /vagrant/.env /home/vagrant/.virtualenvs/$VENV_NAME/bin/postactivate
        source /home/vagrant/.virtualenvs/$VENV_NAME/bin/postactivate
    fi

    # So that we can install things with pip while ssh'd in as vagrant user:
    sudo chown -R vagrant:vagrant /home/vagrant/.virtualenvs/$VENV_NAME/

    # Automatically switch to the virtual env on log in:
    echo "workon $VENV_NAME" >> /home/vagrant/.profile
fi


# If we have a requirements.txt file in this project, then install
# everything in it with pip in a new virtualenv.
if [[ $REQUIREMENTS_FILE ]]; then
    if [[ -f /vagrant/$REQUIREMENTS_FILE ]]; then
        echo "Installing packages from ./${REQUIREMENTS_FILE} with pip"
        pip install -r /vagrant/$REQUIREMENTS_FILE
    fi
fi

echo "=== End Vagrant Provisioning using 'config/vagrant/virtualenv_setup.sh'"
