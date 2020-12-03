#!/bin/bash
USER_ID=$1
GROUP_ID=$2
USERNAME=$3
PASSWD=$4

echo "user:group - $USER_ID:$GROUP_ID"
echo "username:passwd - $USERNAME:$PASSWD"
echo "root:passwd - root:$PASSWD"

su <<< $PASSWD -c "groupadd $USERNAME --gid $GROUP_ID"
if [ $? -ne 0 ]; then
  echo failed to groupadd
  exit -1
fi

echo "groupadd completed"

su <<< $PASSWD -c "useradd $USERNAME --uid $USER_ID --gid $GROUP_ID"
if [ $? -ne 0 ]; then
  echo failed to useradd
  exit -1
fi

echo "useradd completed"

su <<< $PASSWD -c "echo $USERNAME:$PASSWD | chpasswd"

if [ $? -ne 0 ]; then
  echo failed to chpasswd
  exit -1
fi

echo "chpasswd completed"
