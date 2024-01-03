import boto3
import json
from kubernetes import client, config

def get_eks_cluster_endpoint(cluster_name):
    eks_client = boto3.client('eks')

    response = eks_client.describe_cluster(name=cluster_name)
    return response['cluster']['endpoint']

def get_running_pods_count():
    config.load_kube_config()
    k8s_api = client.CoreV1Api()

    pods = k8s_api.list_pod_for_all_namespaces()
    running_pods_count = sum(1 for pod in pods.items if pod.status.phase == 'Running')

    return running_pods_count

def lambda_handler(event, context):
    # Replace 'cc-ndc-eks-cluster-dev-cluster' with your actual EKS cluster name
    cluster_name = 'cc-ndc-eks-cluster-dev-cluster'

    # Get EKS cluster endpoint
    cluster_endpoint = get_eks_cluster_endpoint(cluster_name)

    # Get the number of running pods from Kubernetes API
    running_pods_count = get_running_pods_count()

    # Your custom logic with the pod information goes here

    return {
        'statusCode': 200,
        'body': json.dumps({'ClusterEndpoint': cluster_endpoint, 'RunningPodsCount': running_pods_count})
    }
