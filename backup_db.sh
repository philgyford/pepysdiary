#!/usr/bin/env bash
#
# For backing up the Postgres database to S3.
#
# First do:
#
#     $ sudo apt-get install s3cmd
#     $ s3cmd --configure
#
# Then, if env variables are set, just run with:
#
#     $ ./backup_db.sh
#
# Retrieve a decrypted backup with this (replacing VALUES with correct path):
#
#     $ s3cmd get s3://BUCKET_NAME/APP/APP-backup-DATE_TIME
#
# Expects these ENV variables to be set:
# $DB_NAME
# $DB_USERNAME
# $DB_PASSWORD
# $DB_HOST
#
# Set these to what you need:
BUCKET_NAME=pepysdiary-pg-backups
APP=pepysdiary

TIMESTAMP=$(date +%F_%T | tr ':' '-')
TEMP_FILE=$(mktemp tmp.XXXXXXXXXX)
S3_FILE="s3://$BUCKET_NAME/$APP/$APP-backup-$TIMESTAMP"

PGPASSWORD=$DB_PASSWORD pg_dump -Fc --no-acl -h $DB_HOST -U $DB_USERNAME $DB_NAME > $TEMP_FILE
s3cmd put $TEMP_FILE $S3_FILE --encrypt
rm "$TEMP_FILE"

