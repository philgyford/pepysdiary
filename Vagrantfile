# -*- mode: ruby -*-
# vi: set ft=ruby :
require 'yaml'

unless File.exist?('config/vagrant.yml')
  raise "There is no config/vagrant.yml file.\nCopy config/vagrant.template.yml, make any changes you need, then try again."
end

settings = YAML.load_file 'config/vagrant.yml'

$script = <<SCRIPT
echo Beginning Vagrant provisioning...
date > /etc/vagrant_provisioned_at
SCRIPT

# Vagrantfile API/syntax version. Don't touch unless you know what you're doing!
VAGRANTFILE_API_VERSION = '2'

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|

  config.vm.provision 'shell', inline: $script

  # "ubuntu/xenial64" doesn't have a 'vagrant' user, so:
  config.vm.box = "bento/ubuntu-16.04"

  # Share an additional folder to the guest VM. The first argument is
  # the path on the host to the actual folder. The second argument is
  # the path on the guest to mount the folder. And the optional third
  # argument is a set of non-required options.
  config.vm.synced_folder ".", "/vagrant"

  # Create a forwarded port mapping which allows access to a specific port
  # within the machine from a port on the host machine. In the example below,
  # accessing "localhost:5000" will access port 5000 on the guest machine.
  config.vm.network "forwarded_port", guest: 5000, host: 5000

  # PostgreSQL Server port forwarding
  config.vm.network "forwarded_port", host: 15432, guest: 5432

  config.vm.provider "virtualbox" do |vb|
    vb.customize ["modifyvm", :id,
                  "--name", settings['virtualbox']['name'],
                  "--memory", settings['virtualbox']['memory'] ]
  end

  # You can provision with just one of these scripts by using its name, eg:
  #   $ vagrant provision --provision-with postgresql

  config.vm.provision 'build',
            type: 'shell',
            path: 'config/vagrant/build_dependency_setup.sh',
            args: [
              settings['use_geodjango'],
            ]

  config.vm.provision 'bash',
            type: 'shell',
            path: 'config/vagrant/bash_setup.sh'

  config.vm.provision 'git',
            type: 'shell',
            path: 'config/vagrant/git_setup.sh'

  config.vm.provision 'postgresql',
            type: 'shell',
            path: 'config/vagrant/postgresql_setup.sh',
            args: [
              settings['db']['name'],
              settings['db']['user'],
              settings['db']['password'],
              settings['use_geodjango'],
            ]

  config.vm.provision 'python',
            type: 'shell',
            path: 'config/vagrant/python_setup.sh'

  config.vm.provision 'virtualenv',
            type: 'shell',
            path: 'config/vagrant/virtualenv_setup.sh',
            args: [
              settings['virtualenv']['envname'],
              settings['virtualenv']['requirements_file'],
            ]

  # Will install foreman and, if there's a Procfile, start it:
  config.vm.provision 'foreman',
            type: 'shell',
            path: 'config/vagrant/foreman_setup.sh',
            args: [
              settings['virtualenv']['envname'],
              settings['django']['settings_module'],
              settings['foreman']['procfile'],
              settings['foreman']['start_foreman'],
            ]

  config.vm.provision 'django',
            type: 'shell',
            path: 'config/vagrant/django_setup.sh',
            args: [
              settings['virtualenv']['envname'],
              settings['django']['run_migrations'],
            ]
end
