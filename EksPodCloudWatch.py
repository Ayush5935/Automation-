import boto3
import json
from kubernetes import client, config

def get_eks_cluster_endpoint(cluster_name):
    eks_client = boto3.client('eks')
    response = eks_client.describe_cluster(name=cluster_name)
    return response['cluster']['endpoint']

def get_running_pod_details():
    config.load_kube_config()
    k8s_api = client.CoreV1Api()

    pods = k8s_api.list_pod_for_all_namespaces()
    running_pod_details = []

    for pod in pods.items:
        if pod.status.phase == 'Running':
            running_pod_details.append({
                'Namespace': pod.metadata.namespace,
                'Name': pod.metadata.name,
                'Ready': pod.status.container_statuses[0].ready if pod.status.container_statuses else None,
                'Status': pod.status.phase,
            })

    return running_pod_details

def get_nodes_count():
    config.load_kube_config()
    k8s_api = client.CoreV1Api()

    nodes = k8s_api.list_node()
    return len(nodes.items)

if __name__ == "__main__":
    # Replace 'cc-ndc-eks-cluster-dev-cluster' with your actual EKS cluster name
    cluster_name = 'cc-ndc-eks-cluster-dev-cluster'

    # Get EKS cluster endpoint
    cluster_endpoint = get_eks_cluster_endpoint(cluster_name)

    # Get details for running pods from Kubernetes API
    running_pod_details = get_running_pod_details()

    # Get the count of nodes in the EKS cluster
    nodes_count = get_nodes_count()

    # Print the information
    print(f'EKS Cluster Endpoint: {cluster_endpoint}')
    print('Running Pod Details:')
    for pod in running_pod_details:
        print(f'  Namespace: {pod["Namespace"]}')
        print(f'  Name: {pod["Name"]}')
        print(f'  Ready: {pod["Ready"]}')
        print(f'  Status: {pod["Status"]}')
    print(f'Number of Nodes in the Cluster: {nodes_count}')
