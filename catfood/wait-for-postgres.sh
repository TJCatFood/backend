#!/usr/bin/env bash

set -e
  
host="$1"
shift

POSTGRES_USER="$1"
shift

POSTGRES_PASSWORD="$1"
shift

cmd="$@"
echo $cmd
  
until PGPASSWORD=$POSTGRES_PASSWORD psql -h "$host" -U $POSTGRES_USER -c '\q'; do
  >&2 echo "Postgres is unavailable - sleeping"
  sleep 1
done
  
>&2 echo "Postgres is up - executing command"
exec $cmd

