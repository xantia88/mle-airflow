import datetime

from airflow.models import Variable
from airflow.decorators import dag, task
from vmware import functions

@dag(start_date=datetime.datetime(2021, 1, 1), schedule="@once")
def generate_dag():

    @task
    def extract():
        data = {"id":1}
        print("extract",data)

        functions.request()
        vm_host = Variable.get("vmhost")
        vm_user = Variable.get("vmuser")
        vm_password =Variable.get("vmpassword")
        content = functions.vsphere_connect(vm_host, vm_user, vm_password)

        return data
    
    @task
    def transform(data):
        data2 = {"id":2}
        print("transform",data,data2)
        return data2
    
    @task
    def load(data):
        print("load",data)
        pass
    
    data = extract()
    data = transform(data)
    load(data)
    
generate_dag()
