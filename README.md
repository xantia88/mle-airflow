
# Установка Apache Airflow

Создайте директории в рабочей папке

```
mkdir -p ./dags ./logs ./plugins ./config ./output
```

Задайте параметр ***AIRFLOW_UID*** в файле ***.env***. Если команда возвращает значение 0, задайте параметру значение 50000. 

```
echo -e "AIRFLOW_UID=$(id -u)"
```

Выполните инициализацию образов Apache Airflow.

```
docker compose up airflow-init
```

По рекомендации разработчиков, после инициализации нужно удалить мусор

```
docker compose down --volumes --remove-orphans
```

# Запуск и остановка Apache Airflow

Запустите контейнеры из созданных ранее образов (перед запуском рекомендуется убедиться, что контейнеры уже не запущены, см. "Дополнительные команды")

```
docker compose up
```

Для остановки всех запущенных контейнеров выполните команду ниже из рабочей папки

```
docker compose down
```

# Пользовательский интерфейс

Для доступа в пользовательский интерфейс используйте интернет браузер. Имя пользователя ***airflow***, пароль ***airflow***. Настройка номера порта осуществляется в файле ***docker-compose.yaml***, параметр ***ports*** сервиса ***airflow-webserver***.

```
http://127.0.0.1:8080/
```
# Переменные окружения

Для корректного функционирования Dag необходимо настроить следующие переменные в разделе ***Admin - Variables*** пользовательского интерфейса. Переменные можно настроить вручную или импортировать из файла ***variables.json***

```
vmhost - сетевой адрес VMCenter
vmuser - пользователь для доступа к VMCenter
vmpassword - пароль для доступа к VMCenter
output - папка для записи преобразованных файлов на хост машину
```




