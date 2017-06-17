#!/usr/bin/env bash
#
# For backing up the Postgres database to S3.
#
# Assumes the AWS CLI tool is already installed and configured.
# http://aws.amazon.com/documentation/cli
#
# Test by doing something like:
#
#     $ aws s3 ls s3://BUCKET_NAME/DIRECTORY_NAME
#
# Then, run with:
#
#     $ ./backup_db.sh
#
# Download an uploaded file and then you can restore the dump with:
#
#     $ pg_restore -c -Fc -h localhost -d pepysdiary -U pepysdiary -W FILENAME
#
# -c: Clean - Drop database objects before recreating them.
# -Fc: Format - Should be the same as we use with pg_dump, below (c, d, or t).
# -h: Host
# -d: Database name
# -U: Username
# -W: Ask for password
#
# Expects these ENV variables to be set:
# $DB_NAME
# $DB_USERNAME
# $DB_PASSWORD
# $DB_HOST
#
# Set these to what you need:
BUCKET_NAME=jagged-production-pg-backups
APP=pepysdiary

# Where we put the temporary database dump.
# Must be writable to by the file when run via cron.
TEMP_DIR=/home/deploy

TIMESTAMP=$(date +%F_%T | tr ':' '-')

TEMP_FILE=$(mktemp ${TEMP_DIR}/tmp.XXXXXXXXXX)

S3_FILE="s3://$BUCKET_NAME/$APP/$APP-backup-$TIMESTAMP"

# Dump the database to a file:
PGPASSWORD=$DB_PASSWORD pg_dump -Fc --no-acl -h $DB_HOST -U $DB_USERNAME $DB_NAME > $TEMP_FILE

# Upload to S3
aws s3 cp $TEMP_FILE $S3_FILE

rm "$TEMP_FILE"

