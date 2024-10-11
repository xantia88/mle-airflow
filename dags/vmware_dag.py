import datetime

from airflow.models import Variable
from airflow.decorators import dag, task
from vmware import functions, vcenter


@dag(start_date=datetime.datetime(2024, 1, 1), schedule="@once")
def vmware_dag():

    def get_export_path():
        return Variable.get("output")

    def connect():
        vm_host = Variable.get("vmhost")
        vm_user = Variable.get("vmuser")
        vm_password = Variable.get("vmpassword")
        return vcenter.connect(vm_host, vm_user, vm_password)

    @task
    def datacenters():
        content = connect()
        dcs = vcenter.get_dcs(content)
        dcs_json = vcenter.json(dcs)
        functions.export_dcs(dcs_json, get_export_path())

    @task
    def vms():
        export_path = get_export_path()
        content = connect()
        for dc in vcenter.get_dcs(content):
            vms = vcenter.get_vms(content, dc)
            functions.export_vms(vcenter.json(vms), dc, export_path)

    @task
    def vapps():
        export_path = get_export_path()
        content = connect()
        for dc in vcenter.get_dcs(content):
            vapps = vcenter.get_vapps(content, dc)
            functions.export_vapps(vcenter.json(vapps), dc, export_path)

    @task
    def networks():
        export_path = get_export_path()
        content = connect()
        for dc in vcenter.get_dcs(content):
            networks = vcenter.get_networks(content, dc)
            functions.export_networks(vcenter.json(networks), dc, export_path)

    @task
    def dvswitches():
        export_path = get_export_path()
        content = connect()
        for dc in vcenter.get_dcs(content):
            dvss = vcenter.get_dvswitches(content, dc)
            functions.export_dvswitches(vcenter.json(dvss), dc, export_path)

    @task
    def dvpgroups():
        export_path = get_export_path()
        content = connect()
        for dc in vcenter.get_dcs(content):
            dvpgs = []
            for pg in vcenter.get_dvpgroups(content, dc):
                json_pg = vcenter.convert_to_json(pg)
                json_pg["vlan_id"] = vcenter.getVlans(pg)
                dvpgs.append(json_pg)
            functions.export_dvpgroups(dvpgs, dc, export_path)

    @task
    def hosts():
        pass

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
