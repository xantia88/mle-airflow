import datetime

from airflow.models import Variable
from airflow.decorators import dag, task
from vmware import functions, vcenter


@dag(start_date=datetime.datetime(2024, 1, 1), schedule="@once")
def vmware_dag():

    def connect():
        vm_host = Variable.get("vmhost")
        vm_user = Variable.get("vmuser")
        vm_password = Variable.get("vmpassword")
        return vcenter.connect(vm_host, vm_user, vm_password)

    def get_config():
        return {
            "prefix": Variable.get("prefix", default_var=""),
            "location": Variable.get("location", default_var=""),
            "output": Variable.get("output")
        }

    @task
    def datacenters():
        config = get_config()
        content = connect()
        dcs = vcenter.get_dcs(content)
        json_dcs = vcenter.get_jsons(dcs)
        functions.export_dcs(json_dcs, config)

    @task
    def vms():
        config = get_config()
        content = connect()
        for dc in vcenter.get_dcs(content):
            vms = vcenter.get_vms(content, dc)
            json_vms = vcenter.get_jsons(vms)
            json_dc = vcenter.get_dc_json(dc)
            functions.export_vms(json_vms, json_dc, config)

    @task
    def vapps():
        config = get_config()
        content = connect()
        for dc in vcenter.get_dcs(content):
            vapps = vcenter.get_vapps(content, dc)
            json_vapps = vcenter.get_jsons(vapps)
            json_dc = vcenter.get_dc_json(dc)
            functions.export_vapps(json_vapps, json_dc, config)

    @task
    def networks():
        config = get_config()
        content = connect()
        for dc in vcenter.get_dcs(content):
            networks = vcenter.get_networks(content, dc)
            json_networks = vcenter.get_jsons(networks)
            json_dc = vcenter.get_dc_json(dc)
            functions.export_networks(json_networks, json_dc, config)

    @task
    def dvswitches():
        config = get_config()
        content = connect()
        for dc in vcenter.get_dcs(content):
            dvss = vcenter.get_dvswitches(content, dc)
            json_dvss = vcenter.get_jsons(dvss)
            json_dc = vcenter.get_dc_json(dc)
            functions.export_dvswitches(json_dvss, json_dc, config)

    @task
    def dvpgroups():
        config = get_config()
        content = connect()
        for dc in vcenter.get_dcs(content):
            dvpgs = []
            for pg in vcenter.get_dvpgroups(content, dc):
                json_pg = vcenter.get_pg_json(pg)
                dvpgs.append(json_pg)
            json_dc = vcenter.get_dc_json(dc)
            functions.export_dvpgroups(dvpgs, json_dc, config)

    @task
    def hosts():
        config = get_config()
        content = connect()
        for dc in vcenter.get_dcs(content):
            hosts = []
            for host in vcenter.get_hosts(content, dc):
                json_host = vcenter.get_host_json(host)
                hosts.append(json_host)
            json_dc = vcenter.get_dc_json(dc)
            functions.export_hosts(hosts, json_dc, config)

    @task
    def push():
        pass

    dcs = datacenters()
    vms = vms()
    vapps = vapps()
    networks = networks()
    dvswitches = dvswitches()
    dvpgroups = dvpgroups()
    hosts = hosts()
    push = push()

    dcs >> [vms, vapps, networks,
            dvswitches, dvpgroups, hosts] >> push


vmware_dag()
