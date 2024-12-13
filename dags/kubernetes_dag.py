import datetime
from airflow.operators.bash import BashOperator
from airflow.decorators import dag, task
from kub import kuber, functions
import json
from os import listdir
from os.path import isfile, join


@dag(start_date=datetime.datetime(2024, 1, 1), schedule="@once")
def kubernetes_dag():

    def get_config(section="kubernetes"):
        config = None
        with open("/opt/airflow/config/variables.json") as file:
            config = json.load(file)
        return config[section]

    def get_namespaces(config):
        objects = []
        for cluster in kuber.get_clusters(config):
            cluster_id = cluster["id"]
            namespaces = kuber.get_namespaces(cluster_id, config)
            objects.append(namespaces)
        return objects

    @task
    def clusters():
        config = get_config()
        path = config["output"]
        clusters = kuber.get_clusters(config)
        return functions.save(clusters, path, "clusters")

    @task
    def nodes():
        config = get_config()
        path = config["output"]
        objects = []
        for cluster in kuber.get_clusters(config):
            cluster_id = cluster["id"]
            nodes = kuber.get_nodes(cluster_id, config)
            objects.append(nodes)
        functions.save(objects, path, "nodes")

    @task
    def namespaces():
        config = get_config()
        path = config["output"]
        objects = get_namespaces(config)
        fn = functions.save(objects, path, "namespaces")

    @task
    def persistant_volumes():
        config = get_config()
        path = config["output"]
        objects = []
        for cluster in kuber.get_clusters(config):
            cluster_id = cluster["id"]
            volumes = kuber.get_persistant_volumes(cluster_id, config)
            objects.append(volumes)
        functions.save(objects, path, "volumes")

    @task
    def deployments():
        config = get_config()
        path = config["output"]
        objects = []
        for namespace in get_namespaces(config):
            namespace_id = namespace["id"]
            deployments = kuber.get_deployments(namespace_id, config)
            objects.append(deployments)
        functions.save(objects, path, "deployments")

    @task
    def statefull_sets():
        config = get_config()
        path = config["output"]
        objects = []
        for namespace in get_namespaces(config):
            namespace_id = namespace["id"]
            sets = kuber.get_statefull_sets(namespace_id, config)
            objects.append(sets)
        functions.save(objects, path, "sets")

    @task
    def services():
        config = get_config()
        path = config["output"]
        objects = []
        for namespace in get_namespaces(config):
            namespace_id = namespace["id"]
            services = kuber.get_services(namespace_id, config)
            objects.append(services)
        functions.save(objects, path, "services")

    @task
    def persistant_volume_claims():
        config = get_config()
        path = config["output"]
        objects = []
        for namespace in get_namespaces(config):
            namespace_id = namespace["id"]
            claims = kuber.get_persistance_volume_claims(
                namespace_id, config)
            objects.append(claims)
        functions.save(objects, path, "claims")

    @task
    def network_policies():
        config = get_config()
        path = config["output"]
        objects = []
        for namespace in get_namespaces(config):
            namespace_id = namespace["id"]
            policies = kuber.get_network_policies(namespace_id, config)
            objects.append(policies)
        functions.save(objects, path, "policies")

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

    c = clusters()
    r = root()

    c >> namespaces() >> [deployments(), statefull_sets(), services(),
                          persistant_volume_claims(), network_policies()] >> r >> push
    c >> [nodes(), persistant_volumes()] >> r >> push


kubernetes_dag()
