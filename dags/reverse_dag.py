import datetime

from airflow.decorators import dag, task
from airflow.operators.empty import EmptyOperator
from pyVim.connect import SmartConnect
from pyVmomi import vim, VmomiSupport

@dag(start_date=datetime.datetime(2021, 1, 1), schedule="@once")
def generate_dag():
    #EmptyOperator(task_id="task")

    @task
    def extract():
        data = {"id":1}
        print("extract",data)
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