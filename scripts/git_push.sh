#!/bin/bash

NOW=$( date '+%F_%H:%M:%S' )

SOURCE_DIR=$1

GIT_URL=
GIT_PROJECT=
GIT_USER=
GIT_TOKEN=
GIT_USER_EMAIL=''
GIT_USER_NAME=''
DH_RELOAD=

pwd
ls -la $SOURCE_DIR

rm -r --force --interactive=never $GIT_PROJECT

echo "git clone https://$GIT_USER:$GIT_TOKEN@$GIT_URL/$GIT_PROJECT.git"
git clone https://$GIT_USER:$GIT_TOKEN@$GIT_URL/$GIT_PROJECT.git ./$GIT_PROJECT

cp -v $SOURCE_DIR/*.yaml ./$GIT_PROJECT

cd ./$GIT_PROJECT
git config user.email $GIT_USER_EMAIL
git config user.name $GIT_USER_NAME
ls -la
git add --all
git commit -m "airflow commit "$NOW
git push origin
cd ..

rm -r --force --interactive=never $GIT_PROJECT

curl -X 'PUT' '$DH_RELOAD' -H 'accept: application/json'
