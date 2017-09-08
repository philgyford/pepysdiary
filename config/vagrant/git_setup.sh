#!/usr/bin/env bash

# Via https://github.com/kiere/vagrant-heroku-cedar-14/blob/master/config/vagrant/git_setup.sh

echo "=== Begin Vagrant Provisioning using 'config/vagrant/git_setup.sh'"

# Install Git if not available
if [ -z `which git` ]; then
  echo "===== Installing Git"
  apt-get -y -qq update
  apt-get -y -qq install git-core
fi

echo "=== End Vagrant Provisioning using 'config/vagrant/git_setup.sh'"
