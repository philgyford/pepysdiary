#!/usr/bin/env bash

# Via https://github.com/kiere/vagrant-heroku-cedar-14/blob/master/config/vagrant/build_dependency_setup.sh

echo "=== Begin Vagrant Provisioning using 'config/vagrant/build_dependency_setup.sh'"

USE_GEODJANGO=$1

# Install build dependencies for a sane build environment
apt-get -y -qq update
apt-get -y -qq install autoconf bison build-essential libssl-dev libyaml-dev libreadline6-dev zlib1g-dev libncurses5-dev libffi-dev libgdbm3 libgdbm-dev

# Other things that we may need installed before anything else.
apt-get -y -qq install libmemcached-dev

# So we can install the foreman gem.
apt-get -y -qq install ruby

if [ $USE_GEODJANGO = 'true' ]; then
  # https://docs.djangoproject.com/en/1.11/ref/contrib/gis/install/geolibs/
  echo ""
  echo "Installing Geospatial libraries"
  echo ""
  apt-get -y -qq install binutils libproj-dev gdal-bin
fi

echo "=== End Vagrant Provisioning using 'config/vagrant/build_dependency_setup.sh'"

