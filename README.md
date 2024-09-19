1) Prepare folders on your local machine

mkdir -p ./dags ./logs ./plugins ./config

2) Run the following command to get an AIRFLOW_ID

echo -e "AIRFLOW_UID=$(id -u)"

3) Put AIRFLOW_ID to file .env on your local machine

4) Init airflow container

docker compose up airflow-init

5) Clear cache (recommended by vendor)

docker compose down --volumes --remove-orphans

6) Start container

docker compose up --build

7) Stop container

docker compose down

Access AirFlow from web browser on your local machine:

http://localhost:8080
airflow / airflow
