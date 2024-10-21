#!/bin/bash

NOW=$( date '+%F_%H:%M:%S' )

# Здесь нужно задать настройки
GIT_URL=github.com/xantia88
GIT_PROJECT=draw.io
GIT_USER=xantia88
GIT_TOKEN=

# Вывести информацию о папке, в которой лежат сформированные файлы
ls -la $1

# Клонируем репозиторий во временную папку
rm -r --force --interactive=never $GIT_PROJECT
echo "git clone https://$GIT_USER:$GIT_TOKEN@$GIT_URL/$GIT_PROJECT.git"
git clone https://$GIT_USER:$GIT_TOKEN@$GIT_URL/$GIT_PROJECT.git

# Копируем сформированный файлы во временную папку
cp $1/*.yaml $GIT_PROJECT

# Отправляем файлы в репозиторий на сервер
cd $GIT_PROJECT
git add --all
git commit -m "airflow commit "$NOW
git push origin
cd -

# Удаляем временную папку
rm -r --force --interactive=never $GIT_PROJECT
