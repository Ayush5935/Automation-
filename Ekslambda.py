import os
import boto3
import json
import uuid
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

def assume_role_and_update_dynamodb(cluster_name, is_equal):
    assume_role_arn = 'arn:aws:iam::155880749572:role/DynamoDB_Role'

    sts_client = boto3.client('sts')
    assumed_role = sts_client.assume_role(
        RoleArn=assume_role_arn,
        RoleSessionName='AssumedRoleSession'
    )

    dynamodb = boto3.resource('dynamodb', aws_access_key_id=assumed_role['Credentials']['AccessKeyId'],
                              aws_secret_access_key=assumed_role['Credentials']['SecretAccessKey'],
                              aws_session_token=assumed_role['Credentials']['SessionToken'])

    table_name = 'twistlock-defender-cluster-version'
    table = dynamodb.Table(table_name)

    unique_id = str(uuid.uuid4())
    print(f'Updating DynamoDb item with id {unique_id} and eksclustername {cluster_name}')

    response = table.update_item(
        Key={'id': unique_id, 'eksClusterName': cluster_name},
        UpdateExpression='SET IsEqual = :val',
        ExpressionAttributeValues={':val': is_equal},
        ReturnValues='ALL_NEW'
    )

    updated_item = response.get('Attributes', {})
    print(f'Updated DynamoDB Item: {updated_item}')

def lambda_handler(event, context):
    try:
        cluster_name = 'cc-ndc-eks-cluster-dev-cluster'
        cluster_endpoint = get_eks_cluster_endpoint(cluster_name)
        running_pod_details = get_running_pod_details()
        nodes_count = get_nodes_count()
        is_equal = len(running_pod_details) == nodes_count

        assume_role_and_update_dynamodb(cluster_name, is_equal)

        print(f'Number of Nodes in the Cluster: {nodes_count}')
        print('Running Pod Details:')
        for pod in running_pod_details:
            print(f' Namespace: {pod["Namespace"]}')
            print(f' Name: {pod["Name"]}')
            print(f' Ready: {pod["Ready"]}')
            print(f' Status: {pod["Status"]}')
            print("----------")

        return {
            'statusCode': 200,
            'body': json.dumps({'ClusterEndpoint': cluster_endpoint, 'RunningPodDetails': running_pod_details, 'NodesCount': nodes_count})
        }
    except Exception as e:
        print(f"Error in lambda_handler: {e}")
        raise

# Uncomment the line below to test the lambda locally
# lambda_handler(None, None)
