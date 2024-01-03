import boto3
import json
import time
from kubernetes import client, config

def lambda_handler(event, context):
    # Replace 'your-cluster-name' with your actual EKS cluster name
    cluster_name = 'your-cluster-name'

    # Create an EKS client
    eks_client = boto3.client('eks')

    try:
        # Describe the EKS cluster
        response = eks_client.describe_cluster(name=cluster_name)

        # Get the EKS cluster endpoint
        cluster_endpoint = response['cluster']['endpoint']

        # Load the Kubernetes configuration for the EKS cluster
        config.load_kube_config()
        
        # Create a Kubernetes API client
        k8s_api = client.CoreV1Api()

        # Retrieve pod information
        pods = k8s_api.list_namespaced_pod(namespace='default')

        # Extract relevant information from the pods
        pod_info = {
            'ClusterName': cluster_name,
            'PodCount': len(pods.items),
            'PodDetails': [{'Name': pod.metadata.name, 'Status': pod.status.phase} for pod in pods.items]
        }

        # Your custom logic with the pod information goes here

        return {
            'statusCode': 200,
            'body': json.dumps(pod_info)
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': f'Error: {str(e)}'
        }
￼Enter
