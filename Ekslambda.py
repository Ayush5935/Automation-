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

def update_dynamodb(cluster_name, is_equal):
    dynamodb = boto3.resource('dynamodb')
    table_name = 'YOUR_DYNAMODB_TABLE_NAME'  # Replace with your actual DynamoDB table name
    table = dynamodb.Table(table_name)

    response = table.update_item(
        Key={'ClusterName': cluster_name},
        UpdateExpression='SET IsEqual = :val',
        ExpressionAttributeValues={':val': is_equal},
        ReturnValues='UPDATED_NEW'
    )

def lambda_handler(event, context):
    try:
        # Replace 'cc-ndc-eks-cluster-dev-cluster' with your actual EKS cluster name
        cluster_name = 'cc-ndc-eks-cluster-dev-cluster'

        # Get EKS cluster endpoint
        cluster_endpoint = get_eks_cluster_endpoint(cluster_name)

        # Get details for running pods from Kubernetes API
        running_pod_details = get_running_pod_details()

        # Get the count of nodes in the EKS cluster
        nodes_count = get_nodes_count()

        # Check if the number of running pods is equal to the number of nodes
        is_equal = len(running_pod_details) == nodes_count

        # Call the function to update DynamoDB based on the condition
        update_dynamodb(cluster_name, is_equal)

        # Print the information
        print(f'EKS Cluster Endpoint: {cluster_endpoint}')
        print('Running Pod Details:')
        for pod in running_pod_details:
            print(f'  Namespace: {pod["Namespace"]}')
            print(f'  Name: {pod["Name"]}')
            print(f'  Ready: {pod["Ready"]}')
            print(f'  Status: {pod["Status"]}')
        print(f'Number of Nodes in the Cluster: {nodes_count}')

        # If you want to perform additional logic or actions based on the pod information and node count, do it here

        return {
            'statusCode': 200,
            'body': json.dumps({'ClusterEndpoint': cluster_endpoint, 'RunningPodDetails': running_pod_details, 'NodesCount': nodes_count})
        }
    except Exception as e:
        print(f"Error in lambda_handler: {e}")
        raise

# Uncomment the next line to run the Lambda function locally
# lambda_handler(None, None)
￼Enter
