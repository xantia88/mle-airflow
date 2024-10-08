import datetime

from airflow.models import Variable
from airflow.decorators import dag, task
from vmware import functions

@dag(start_date=datetime.datetime(2024, 1, 1), schedule="@once")
def vmware_dag():

    @task
    def extract():
        print("extract", data)
        vm_host = Variable.get("vmhost")
        print("vm_host", vm_host)
        vm_user = Variable.get("vmuser")
        print("vm_user", vm_user)
        vm_password = Variable.get("vmpassword")
        content = functions.vsphere_connect(vm_host, vm_user, vm_password)
        return content

    @task
    def datacenters(data):
        type = "dc"
        transformed = {"type": type, "content": data}
        print(type, data, transformed)
        return transformed

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

    data = extract()
    datacenters = datacenters(data)
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
