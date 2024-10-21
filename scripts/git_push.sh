#!/bin/bash

# Настройки
GIT_URL=
GIT_USER=
GIT_TOKEN=
GIT_PROJECT=
GIT_USER_EMAIL=""
GIT_USER_NAME=""

# Вывести информацию о папке, в которой лежат сформированные файлы
echo "Output dir:"$1
ls -la $1

# Клонировать репозиторий
rm -r --force --interactive=never $GIT_PROJECT
echo "git clone https://$GIT_USER:$GIT_TOKEN@$GIT_URL/$GIT_PROJECT.git"
git clone https://$GIT_USER:$GIT_TOKEN@$GIT_URL/$GIT_PROJECT.git

# Настроить репозиторий
cd $GIT_PROJECT
echo "Repo dir:"$( pwd )
git config user.email $GIT_USER_EMAIL
git config user.name $GIT_USER_NAME

# Скопировать файлы
echo "Copy from:"$1
cp $1/*.yaml .
ls -la

# Отправляем файлы в репозиторий на сервер
git add --all
git commit -m "airflow commit "$( date '+%F_%H:%M:%S' )
git push origin
