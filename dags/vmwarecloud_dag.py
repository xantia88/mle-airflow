import datetime
from airflow.operators.bash import BashOperator
from airflow.decorators import dag, task
from vmwarecloud import functions
import json
from os import listdir
from os.path import isfile, join


@dag(start_date=datetime.datetime(2024, 1, 1), schedule="@once")
def vmwarecloud_dag():

    def get_config(section="vmwarecloud"):
        config = None
        with open("/opt/airflow/config/variables.json") as file:
            config = json.load(file)
        return config[section]

    def init_config():
        config = get_config()
        return functions.init_config(config["script_path"], config["config_file"])

    @task
    def orgs():
        config = init_config()
        if config:
            functions.export_orgs(config)

    @task
    def vdcs():
        config = init_config()
        if config:
            functions.export_vdcs(config)

    @task
    def vdcgroups():
        config = init_config()
        if config:
            functions.export_vdcgroups(config)

    @task
    def orgnetworks():
        config = init_config()
        if config:
            functions.export_orgnetworks(config)

    @task
    def edgegw():
        config = init_config()
        if config:
            functions.export_edgegw(config)

    @task
    def vms():
        config = init_config()
        if config:
            functions.export_vms(config)

    @task
    def vapps():
        config = init_config()
        if config:
            functions.export_vapps(config)

    @task
    def vappnets():
        config = init_config()
        if config:
            functions.export_vappnets(config)

    @task
    def edgenat():
        config = init_config()
        if config:
            functions.export_edgefw(config)

    @task
    def root():
        config = get_config()
        path = config["output"]
        objects = {
            "imports": [f for f in listdir(path) if isfile(join(path, f))]
        }
        functions.save(objects, path, "root")

    git = get_config("git")
    push = BashOperator(
        task_id="push",
        bash_command="{} {} ".format(
            git.get("push_script"), git.get("output_dir"))
    )

    orgs = orgs()
    vdcs = vdcs()
    vdcgroups = vdcgroups()
    orgnetworks = orgnetworks()
    edgegw = edgegw()
    vms = vms()
    vapps = vapps()
    vappnets = vappnets()
    edgenat = edgenat()
    r = root()

    [orgs, vdcs, vdcgroups, orgnetworks, edgegw,
        vms, vapps, vappnets, edgenat] >> r >> push


vmwarecloud_dag()
