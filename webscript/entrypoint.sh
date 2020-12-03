#!/bin/bash

/code/script/chown.sh `id -u` `id -g` /code mypasswd
if [ $? -ne 0 ]; then
  echo "failed to chown /code"
fi

/code/script/chown.sh `id -u` `id -g` /home/code mypasswd
if [ $? -ne 0 ]; then
  echo "failed to chown /home/code"
fi

/code/script/useradd.sh `id -u` `id -g` code mypasswd
if [ $? -ne 0 ]; then
  echo "failed to useradd code"
fi

$@
