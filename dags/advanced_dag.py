import datetime
from airflow.operators.bash import BashOperator
from airflow.decorators import dag, task
from advanced import functions
import json
from os import listdir
from os.path import isfile, join


@dag(start_date=datetime.datetime(2024, 1, 1), schedule="@once")
def advanced_dag():

    def get_config(section="advanced"):
        config = None
        with open("/opt/airflow/config/variables.json") as file:
            config = json.load(file)
        return config[section]

    @task
    def dms():
        config = get_config()
        if config:
            functions.export_dms(config)

    @task
    def secgroups():
        config = get_config()
        if config:
            functions.export_secgroups(config)

    @task
    def cces():
        config = get_config()
        if config:
            functions.export_cces(config)

    @task
    def nat_gateways():
        config = get_config()
        if config:
            functions.export_nat_gateways(config)

    @task
    def elbs():
        config = get_config()
        if config:
            functions.export_elbs(config)

    @task
    def servers():
        config = get_config()
        if config:
            functions.export_servers(config)

    @task
    def vpcs():
        config = get_config()
        if config:
            functions.export_vpcs(config)

    @task
    def subnets():
        config = get_config()
        if config:
            functions.export_subnets(config)

    @task
    def peerings():
        config = get_config()
        if config:
            functions.export_peerings(config)

    @task
    def eips():
        config = get_config()
        if config:
            functions.export_eips(config)

    @task
    def vaults():
        config = get_config()
        if config:
            functions.export_vaults(config)

    @task
    def backup_policies():
        config = get_config()
        if config:
            functions.export_backup_policies(config)

    @task
    def rdss():
        config = get_config()
        if config:
            functions.export_rdss(config)

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

    dms = dms()
    secgroups = secgroups()
    cces = cces()
    nat_gateways = nat_gateways()
    elbs = elbs()
    servers = servers()
    vpcs = vpcs()
    subnets = subnets()
    peerings = peerings()
    eips = eips()
    vaults = vaults()
    backaup_policies = backup_policies()
    rdss = rdss()
    r = root()

    [dms, secgroups, cces, nat_gateways, elbs, servers, vpcs, subnets,
        peerings, eips, vaults, backaup_policies, rdss] >> r >> push


advanced_dag()
