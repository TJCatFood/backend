#!/bin/bash
USER_ID=$1
GROUP_ID=$2
DIR=$3
PASSWD=$4

echo "user:group - $USER_ID:$GROUP_ID"
echo "root:passwd - root:$PASSWD"
echo "dir - $DIR"

su <<<$PASSWD -c "chown -R $USER_ID:$GROUP_ID $DIR"

if [ $? -ne 0 ]; then
  echo failed to chown
  exit -1
fi

echo "chown completed"
