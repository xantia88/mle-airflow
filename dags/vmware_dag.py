import datetime

from airflow.models import Variable
from airflow.decorators import dag, task
from vmware import functions


@dag(start_date=datetime.datetime(2024, 1, 1), schedule="@once")
def vmware_dag():

    def get_content():
        vm_host = Variable.get("vmhost")
        vm_user = Variable.get("vmuser")
        vm_password = Variable.get("vmpassword")
        return functions.vsphere_connect(vm_host, vm_user, vm_password)

    @task
    def datacenters():
        content = get_content()
        return functions.get_datacenters(content)

    @task
    def vms(data):
        type = "vms"
        transformed = {"type": type}
        print(type, data, transformed)
        return transformed

    @task
    def vapps(data):
        type = "vapps"
        transformed = {"type": type}
        print(type, data, transformed)
        return transformed

    @task
    def networks(data):
        type = "networks"
        transformed = {"type": type}
        print(type, data, transformed)
        return transformed

    @task
    def dvswitch(data):
        type = "dswitch"
        transformed = {"type": type}
        print(type, data, transformed)
        return transformed

    @task
    def dvportgroup(data):
        type = "dvportgroup"
        transformed = {"type": type}
        print(type, data, transformed)
        return transformed

    @task
    def hosts(data):
        type = "hosts"
        transformed = {"type": type}
        print(type, data, transformed)
        return transformed

    @task
    def save(objects):
        print()
        output = Variable.get("output")
        print("save", len(objects), "objects")
        for object in objects:
            print("save", object["type"])
            functions.save(object, output, object["type"])
        return output

    @task
    def push(folder):
        print("push to git", folder)

    datacenters = datacenters()
    objects = [
        datacenters,
        vms(datacenters),
        vapps(datacenters),
        networks(datacenters),
        dvswitch(datacenters),
        dvportgroup(datacenters),
        hosts(datacenters),
    ]
    folder = save(objects)
    push(folder)


vmware_dag()
