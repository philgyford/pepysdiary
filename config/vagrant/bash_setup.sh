#!/usr/bin/env bash

echo "=== Begin Vagrant Provisioning using 'config/vagrant/bash_setup.sh'"

######################################################################
# Will make up-arrow only fetch previous commands based on what we've already typed:
cat > /home/vagrant/.inputrc <<EOF
"\e[A": history-search-backward
"\e[B": history-search-forward
set show-all-if-ambiguous on
set completion-ignore-case on
EOF

echo "=== End Vagrant Provisioning using 'config/vagrant/bash_setup.sh'"

