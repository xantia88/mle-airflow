1. Prepare folders on your local machine

mkdir -p ./dags ./logs ./plugins ./config

2. Init airflow

docker compose up airflow-init

3. Clear cache

docker compose down --volumes --remove-orphans

4. Start container

docker compose up --build

5. Stop container

docker compose down


Access AirFlow from web browser:

http://<your host ip address>:8080
airflow / airflow
