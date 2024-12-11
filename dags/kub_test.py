from kub import kuber, functions
import json


def kubernetes_dag_test():

    def get_config(section="kubernetes"):
        config = None
        with open("../config/variables.json") as file:
            config = json.load(file)
        return config[section]

    def get_namespaces(config):
        objects = []
        for cluster in kuber.get_clusters(config):
            cluster_id = cluster["id"]
            namespaces = kuber.get_namespaces(cluster_id, config)
            objects.append(namespaces)
        return objects

    def clusters():
        config = get_config()
        path = config["output"]
        clusters = kuber.get_clusters(config)
        functions.save(clusters, path, "clusters")

    def nodes():
        config = get_config()
        path = config["output"]
        objects = []
        for cluster in kuber.get_clusters(config):
            cluster_id = cluster["id"]
            nodes = kuber.get_nodes(cluster_id, config)
            objects.append(nodes)
        functions.save(objects, path, "nodes")

    def namespaces():
        config = get_config()
        path = config["output"]
        objects = get_namespaces(config)
        functions.save(objects, path, "namespaces")

    def persistant_volumes():
        config = get_config()
        path = config["output"]
        objects = []
        for cluster in kuber.get_clusters(config):
            cluster_id = cluster["id"]
            volumes = kuber.get_persistant_volumes(cluster_id, config)
            objects.append(volumes)
        functions.save(objects, path, "volumes")

    def deployments():
        config = get_config()
        path = config["output"]
        objects = []
        for namespace in get_namespaces(config):
            namespace_id = namespace["id"]
            deployments = kuber.get_deployments(namespace_id, config)
            objects.append(deployments)
        functions.save(objects, path, "deployments")

    def statefull_sets():
        config = get_config()
        path = config["output"]
        objects = []
        for namespace in get_namespaces(config):
            namespace_id = namespace["id"]
            sets = kuber.get_statefull_sets(namespace_id, config)
            objects.append(sets)
        functions.save(objects, path, "sets")

    def services():
        config = get_config()
        path = config["output"]
        objects = []
        for namespace in get_namespaces(config):
            namespace_id = namespace["id"]
            services = kuber.get_services(namespace_id, config)
            objects.append(services)
        functions.save(objects, path, "services")

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

    def network_policies():
        config = get_config()
        path = config["output"]
        objects = []
        for namespace in get_namespaces(config):
            namespace_id = namespace["id"]
            policies = kuber.get_network_policies(namespace_id, config)
            objects.append(policies)
        functions.save(objects, path, "policies")

    clusters()

    nodes()
    namespaces()
    persistant_volumes()

    deployments()
    statefull_sets()
    services()
    persistant_volume_claims()
    network_policies()


if __name__ == "__main__":
    kubernetes_dag_test()
