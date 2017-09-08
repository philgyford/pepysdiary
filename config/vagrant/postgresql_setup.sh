#!/bin/sh -e

# Expects three arguments:
#   $1 - database name
#   $2 - database user
#   #3 - database user password

# Via https://github.com/kiere/vagrant-heroku-cedar-14/blob/master/config/vagrant/postgresql_setup.sh

echo "=== Begin Vagrant Provisioning using 'config/vagrant/postgresql_setup.sh'"

APP_DB_NAME=$1
APP_DB_USER=$2
APP_DB_PASS=$3
USE_GEODJANGO=$4

# Edit the following to change the version of PostgreSQL that is installed
PG_VERSION=9.6

# Edit the following to change the version of PostGIS that is installed if
# USE_GEODJANGO is true.
POSTGIS_VERSION=2.3

###########################################################
# Changes below this line are probably not necessary
###########################################################
print_db_usage () {
  echo "Your PostgreSQL database has been setup and can be accessed on your local machine on the forwarded port (default: 15432)"
  echo "  Host: localhost"
  echo "  Port: 15432"
  echo "  Database: $APP_DB_NAME"
  echo "  Username: $APP_DB_USER"
  echo "  Password: $APP_DB_PASS"
  echo ""
  echo "Admin access to postgres user via VM:"
  echo "  vagrant ssh"
  echo "  sudo su - postgres"
  echo ""
  echo "psql access to app database user via VM:"
  echo "  vagrant ssh"
  echo "  sudo su - postgres"
  echo "  PGUSER=$APP_DB_USER PGPASSWORD=$APP_DB_PASS psql -h localhost $APP_DB_NAME"
  echo ""
  echo "Env variable for application development:"
  echo "  DATABASE_URL=postgresql://$APP_DB_USER:$APP_DB_PASS@localhost:15432/$APP_DB_NAME"
  echo ""
  echo "Local command to access the database via psql:"
  echo "  PGUSER=$APP_DB_USER PGPASSWORD=$APP_DB_PASS psql -h localhost -p 15432 $APP_DB_NAME"
}

export DEBIAN_FRONTEND=noninteractive

PROVISIONED_ON=/etc/vm_provision_on_timestamp
if [ -f "$PROVISIONED_ON" ]
then
  echo "VM was already provisioned at: $(cat $PROVISIONED_ON)"
  echo "To run system updates manually login via 'vagrant ssh' and run 'apt-get update && apt-get upgrade'"
  echo ""
  print_db_usage
  exit
fi

PG_REPO_APT_SOURCE=/etc/apt/sources.list.d/pgdg.list
if [ ! -f "$PG_REPO_APT_SOURCE" ]
then
  # Add PG apt repo:
  echo "deb http://apt.postgresql.org/pub/repos/apt/ trusty-pgdg main" > "$PG_REPO_APT_SOURCE"

  # Add PGDG repo key:
  wget --quiet -O - http://apt.postgresql.org/pub/repos/apt/ACCC4CF8.asc | apt-key add -
fi

# Update package list and upgrade all packages
apt-get update
apt-get -y -qq upgrade

apt-get -y -qq install "postgresql-$PG_VERSION" "postgresql-contrib-$PG_VERSION" libpq-dev

if [ $USE_GEODJANGO = 'true' ]
then
  echo ""
  echo "Installing PostGIS"
  echo ""
  # NOTE: GEOS, PROJ.4 and GDAL should be installed before this.
  apt-get -y -qq install postgresql-$PG_VERSION-postgis-$POSTGIS_VERSION postgresql-$PG_VERSION-postgis-$POSTGIS_VERSION-scripts postgresql-server-dev-$PG_VERSION python-psycopg2
fi

PG_CONF="/etc/postgresql/$PG_VERSION/main/postgresql.conf"
PG_HBA="/etc/postgresql/$PG_VERSION/main/pg_hba.conf"
PG_DIR="/var/lib/postgresql/$PG_VERSION/main"

# Edit postgresql.conf to change listen address to '*':
sed -i "s/#listen_addresses = 'localhost'/listen_addresses = '*'/" "$PG_CONF"

# Append to pg_hba.conf to add password auth:
echo "host    all             all             all                     md5" >> "$PG_HBA"

# Explicitly set default client_encoding
echo "client_encoding = utf8" >> "$PG_CONF"

# Restart so that all new config is loaded:
service postgresql restart

cat << EOF | su - postgres -c psql
-- Create the database user:
CREATE USER $APP_DB_USER PASSWORD '$APP_DB_PASS';
EOF

# So that Django tests can create a test database:
cat << EOF | su - postgres -c psql
ALTER USER $APP_DB_USER CREATEDB;
EOF

cat << EOF | su - postgres -c psql
-- Create the database:
CREATE DATABASE "$APP_DB_NAME" WITH OWNER=$APP_DB_USER
                                  LC_COLLATE='en_US.utf8'
                                  LC_CTYPE='en_US.utf8'
                                  ENCODING='UTF8'
                                  TEMPLATE=template0;
EOF

# Django will try to create the postgis extension again, even though it's
# not necessary. To do so, it needs to be a superuser, so we have to make it
# one. It's not possible to do this temporarily because it needs it to
# create test DBs too, so unfortunately it has to stay.
if [ $USE_GEODJANGO = 'true' ]
then
  cat << EOF | su - postgres -c psql $APP_DB_NAME
  CREATE EXTENSION postgis;
  ALTER USER $APP_DB_USER SUPERUSER;
EOF
fi

# Tag the provision time:
date > "$PROVISIONED_ON"

echo "Successfully created PostgreSQL dev virtual machine."
echo ""
print_db_usage

echo "=== End Vagrant Provisioning using 'config/vagrant/postgresql_setup.sh'"
