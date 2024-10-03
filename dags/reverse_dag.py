import datetime

from airflow.models import Variable
from airflow.decorators import dag, task
from vmware import functions

@dag(start_date=datetime.datetime(2024, 1, 1), schedule="@once")
def generate_dag():

    @task
    def extract():
        data = {"id":1}
        print("extract",data)

        #functions.request()
        #vm_host = Variable.get("vmhost")
        #vm_user = Variable.get("vmuser")
        #vm_password =Variable.get("vmpassword")
        #content = functions.vsphere_connect(vm_host, vm_user, vm_password)

        return data
    
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
        print("save", len(objects), "objects")
        for object in objects:
            print("save", object["type"])
        output = Variable.get("output")
        functions.save(objects, output, "architecture")

    @task
    def push(folder):
        print("push to git", folder)

    data = extract()
    objects = [vms(data),
        vapps(data),
        networks(data),
        dvswitch(data),
        dvportgroup(data),
        hosts(data)]
    folder = save(objects)
    push(folder)
    
generate_dag()
