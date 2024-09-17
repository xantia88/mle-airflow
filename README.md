Prepare folders on your local machine

mkdir -p ./dags ./logs ./plugins ./config

Init airflow

docker compose up airflow-init

Clear cache

docker compose down --volumes --remove-orphans

Start container

docker compose up --build

Stop container

docker compose down


Access AirFlow from web browser:

http://<your host ip address>:8080
airflow / airflow
