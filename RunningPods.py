import boto3
import json
from kubernetes import client, config
from datetime import datetime, timezone

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
            pod_age = datetime.now(timezone.utc) - pod.metadata.creation_timestamp
            running_pod_details.append({
                'Namespace': pod.metadata.namespace,
                'Name': pod.metadata.name,
                'Ready': pod.status.container_statuses[0].ready if pod.status.container_statuses else None,
                'Status': pod.status.phase,
                'RestartCount': pod.status.container_statuses[0].restart_count if pod.status.container_statuses else None,
                'Age': str(pod_age),
            })

    return running_pod_details

def lambda_handler(event, context):
    # Replace 'cc-ndc-eks-cluster-dev-cluster' with your actual EKS cluster name
    cluster_name = 'cc-ndc-eks-cluster-dev-cluster'

    # Get EKS cluster endpoint
    cluster_endpoint = get_eks_cluster_endpoint(cluster_name)

    # Get details for running pods from Kubernetes API
    running_pod_details = get_running_pod_details()

    # Your custom logic with the pod information goes here
    # For example, you can print the information
    print(f'EKS Cluster Endpoint: {cluster_endpoint}')
    print('Running Pod Details:')
    for pod in running_pod_details:
        print(f'  Namespace: {pod["Namespace"]}')
        print(f'  Name: {pod["Name"]}')
        print(f'  Ready: {pod["Ready"]}')
        print(f'  Status: {pod["Status"]}')
        print(f'  Restart Count: {pod["RestartCount"]}')
        print(f'  Age: {pod["Age"]}')
        print('---')

    # If you want to perform additional logic or actions based on the pod information, do it here

    return {
        'statusCode': 200,
        'body': json.dumps({'ClusterEndpoint': cluster_endpoint, 'RunningPodDetails': running_pod_details})
    }

# Uncomment the next line to run the Lambda function locally
# lambda_handler(None, None)
