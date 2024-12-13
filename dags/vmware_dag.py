import datetime
from airflow.models import Variable
from airflow.operators.bash import BashOperator
from airflow.decorators import dag, task
from vmware import functions, vcenter
import json
from os import listdir
from os.path import isfile, join


@dag(start_date=datetime.datetime(2024, 1, 1), schedule="@once")
def vmware_dag():

    def get_config():
        config = None
        with open("/opt/airflow/config/variables.json") as file:
            config = json.load(file)
        return config

    def connect(config):
        print("config", config)
        vm_host = config.get("vmhost")
        # get parameter from Airflow variables (Admin / Variables in UI)
        vm_user = Variable.get(config.get("vmuser"))
        vm_password = Variable.get(config.get("vmpassword"))
        print("connect", vm_host, vm_user, vm_password)
        return vcenter.connect(vm_host, vm_user, vm_password)

    @task
    def datacenters():
        configs = get_config()
        print("all_config", configs)
        for config in configs.get("vcenters"):
            content = connect(config)
            dcs = vcenter.get_dcs(content)
            json_dcs = vcenter.get_jsons(dcs)
            functions.export_dcs(json_dcs, config)

    @task
    def vms():
        configs = get_config()
        for config in configs.get("vcenters"):
            content = connect(config)
            for dc in vcenter.get_dcs(content):
                vms = vcenter.get_vms(content, dc)
                json_vms = vcenter.get_jsons(vms)
                json_dc = vcenter.get_dc_json(dc)
                functions.export_vms(json_vms, json_dc, config)

    @task
    def vapps():
        configs = get_config()
        for config in configs.get("vcenters"):
            content = connect(config)
            for dc in vcenter.get_dcs(content):
                vapps = vcenter.get_vapps(content, dc)
                json_vapps = vcenter.get_jsons(vapps)
                json_dc = vcenter.get_dc_json(dc)
                functions.export_vapps(json_vapps, json_dc, config)

    @task
    def networks():
        configs = get_config()
        for config in configs.get("vcenters"):
            content = connect(config)
            for dc in vcenter.get_dcs(content):
                networks = vcenter.get_networks(content, dc)
                json_networks = vcenter.get_jsons(networks)
                json_dc = vcenter.get_dc_json(dc)
                functions.export_networks(json_networks, json_dc, config)

    @task
    def dvswitches():
        configs = get_config()
        for config in configs.get("vcenters"):
            content = connect(config)
            for dc in vcenter.get_dcs(content):
                dvss = vcenter.get_dvswitches(content, dc)
                json_dvss = vcenter.get_jsons(dvss)
                json_dc = vcenter.get_dc_json(dc)
                functions.export_dvswitches(json_dvss, json_dc, config)

    @task
    def dvpgroups():
        configs = get_config()
        for config in configs.get("vcenters"):
            content = connect(config)
            for dc in vcenter.get_dcs(content):
                dvpgs = []
                for pg in vcenter.get_dvpgroups(content, dc):
                    json_pg = vcenter.get_pg_json(pg)
                    dvpgs.append(json_pg)
                json_dc = vcenter.get_dc_json(dc)
                functions.export_dvpgroups(dvpgs, json_dc, config)

    @task
    def hosts():
        configs = get_config()
        for config in configs.get("vcenters"):
            content = connect(config)
            for dc in vcenter.get_dcs(content):
                hosts = []
                for host in vcenter.get_hosts(content, dc):
                    json_host = vcenter.get_host_json(host)
                    hosts.append(json_host)
                json_dc = vcenter.get_dc_json(dc)
                functions.export_hosts(hosts, json_dc, config)

    @task
    def root():
        configs = get_config()
        for config in configs:
            path = config["output"]
            objects = {
                "imports": [f for f in listdir(path) if isfile(join(path, f))]
            }
            functions.save(objects, path, "root")

    configs = get_config()
    git = configs.get("git")
    push = BashOperator(
        task_id="push",
        bash_command="{} {} ".format(
            git.get("push_script"), git.get("output_dir"))
    )

    dcs = datacenters()
    vms = vms()
    vapps = vapps()
    networks = networks()
    dvswitches = dvswitches()
    dvpgroups = dvpgroups()
    hosts = hosts()
    r = root()

    dcs >> [vms, vapps, networks,
            dvswitches, dvpgroups, hosts] >> r >> push


vmware_dag()
