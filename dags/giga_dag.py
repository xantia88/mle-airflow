import datetime
from airflow.operators.bash import BashOperator
from airflow.decorators import dag, task
import json


@dag(start_date=datetime.datetime(2024, 1, 1), schedule="@once")
def giga_dag():

    def get_config(section="gigachat"):
        config = None
        with open("/opt/airflow/config/variables.json") as file:
            config = json.load(file)
        return config[section]

    @task
    def last():
        config = get_config()
        # get last version

    @task
    def previous():
        config = get_config()
        # get version bedfore last

    @task
    def diff():
        config = get_config()
        # prepare analytical statement using gigachat

    @task
    def publish():
        config = get_config()
        # publish analytical statement somewhere

    [last(), previous()] >> diff() >> publish()


giga_dag()
