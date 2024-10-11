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
        dcs = vcenter.get_datacenters(content)
        dcs_json = vcenter.json(dcs)
        functions.export_datacenters(dcs_json, get_export_path())

    @task
    def vms():
        export_path = get_export_path()
        content = connect()
        dcs = vcenter.get_datacenters(content)
        for dc in dcs:
            vms = vcenter.get_vms(content, dc)
            functions.export_vms(vcenter.json(vms), dc, export_path)

    @task
    def vapps():
        pass

    @task
    def networks():
        pass

    @task
    def dvswitch():
        pass

    @task
    def dvportgroup():
        pass

    @task
    def hosts():
        pass

    @task
    def push():
        pass

    t_dcs = datacenters()
    t_vms = vms()
    t_vapps = vapps()
    t_networks = networks()
    t_dvswitch = dvswitch()
    t_dvportgroup = dvportgroup()
    t_hosts = hosts()
    t_push = push()

    t_dcs >> [t_vms, t_vapps, t_networks,
              t_dvswitch, t_dvportgroup, t_hosts] >> t_push


vmware_dag()
