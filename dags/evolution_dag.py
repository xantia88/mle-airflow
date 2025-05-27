import datetime
from airflow.operators.bash import BashOperator
from airflow.decorators import dag, task
from evolution import functions
import json


@dag(start_date=datetime.datetime(2024, 1, 1), schedule="@once")
def evolution_dag():

    def get_config(section="evolution"):
        config = None
        with open("/opt/airflow/config/variables.json") as file:
            config = json.load(file)
        return config[section]

    @task   
    def orgs():
        config = get_config()
        access_token = functions.get_access_token(config)
        functions.export_orgs(config, access_token)
    
    @task
    def vms():
        config = get_config()
        access_token = functions.get_access_token(config)
        functions.export_vms(config, access_token)        

    @task
    def vpcs():
        config = get_config()
        access_token = functions.get_access_token(config)
        functions.export_vpcs(config, access_token)

    @task
    def networks():
        config = get_config()
        access_token = functions.get_access_token(config)
        functions.export_networks(config, access_token)

    @task
    def push():
        configs = get_config()

        bash_cmd_2run = []
        configs = get_config()
        for config in configs.get("vcenters"):
            git_push_script = config["git_push_script"]
            git_output_dir = config["git_output_dir"]
            bash_2run = BashOperator(
                task_id="git_push_" + config["vmhost"],
                bash_command="{} {} ".format(git_push_script, git_output_dir)
            )
            bash_cmd_2run.append(bash_2run)

    orgs = orgs()
    vms = vms()
    vpcs = vpcs()
    networks = networks()
    push = push()
    
    [orgs, vms, vpcs, networks] >> push

evolution_dag()
