#!/bin/bash

# Install python and required python modules.
# pip and virtualenv are in virtualenv_setup.sh

# Initial part of this via
# https://github.com/torchbox/vagrant-django-base/blob/master/install.sh

echo "=== Begin Vagrant Provisioning using 'config/vagrant/python_setup.sh'"

apt-get -qq -y update


# Python dev packages
apt-get -qq -y install python python-dev python-setuptools python-pip

# Install Python 3 if the runtime.txt file specifies it.
if [[ -f /vagrant/runtime.txt ]]; then
  python_runtime=$(head -n 1 /vagrant/runtime.txt)
  if [[ $python_runtime =~ ^python-3\.5 ]]; then
    apt-get -qq -y update
    apt-get -qq  -y install python3.5 python3.5-dev
  fi
  if [[ $python_runtime =~ ^python-3\.6 ]]; then
    # Python 3.6 isn't available in Ubuntu 16.04, so:
    add-apt-repository ppa:fkrull/deadsnakes
    apt-get -qq -y update
    apt-get -qq  -y install python3.6 python3.6-dev
  fi
fi

# Dependencies for image processing with Pillow (drop-in replacement for PIL)
# supporting: jpeg, tiff, png, freetype, littlecms
apt-get -qq install -y libjpeg-dev libtiff-dev zlib1g-dev libfreetype6-dev liblcms2-dev

echo "=== End Vagrant Provisioning using 'config/vagrant/python_setup.sh'"
