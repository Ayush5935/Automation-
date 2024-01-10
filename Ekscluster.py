import os
import boto3
import json
from kubernetes import client, config

def get_clusters():
    eks_client = boto3.client('eks')
    response = eks_client.list_clusters()
    return response['clusters']

def get_eks_cluster_endpoint(cluster_name):
    eks_client = boto3.client('eks')
    response = eks_client.describe_cluster(name=cluster_name)
    return response['cluster']['endpoint']

def get_running_twistlock_pods(cluster_name):
    config.load_kube_config()
    k8s_api = client.CoreV1Api()
    pods = k8s_api.list_pod_for_all_namespaces()
    twistlock_running_pods = []

    for pod in pods.items:
        if pod.status.phase == 'Running' and pod.metadata.namespace == 'twistlock':
            twistlock_running_pods.append(pod.metadata.name)

    return twistlock_running_pods

def get_nodes_count():
    config.load_kube_config()
    k8s_api = client.CoreV1Api()
    nodes = k8s_api.list_node()
    return len(nodes.items)

def assume_role_and_update_dynamodb(cluster_name, is_ok, nodes_count, unique_id):
    assume_role_arn = 'arn:aws:iam::155880749572:role/5g-defender-installation-automation'
    sts_client = boto3.client('sts')
    assumed_role = sts_client.assume_role(
        RoleArn=assume_role_arn,
        RoleSessionName='AssumedRoleSession'
    )

    dynamodb = boto3.resource(
        'dynamodb',
        aws_access_key_id=assumed_role['Credentials']['AccessKeyId'],
        aws_secret_access_key=assumed_role['Credentials']['SecretAccessKey'],
        aws_session_token=assumed_role['Credentials']['SessionToken']
    )

    table_name = 'twistlock-defender-cluster-version'
    table = dynamodb.Table(table_name)

    print(f'Updating DynamoDb item with id {unique_id} and eksclustername {cluster_name}')

    response = table.update_item(
        Key={'id': unique_id, 'eksClusterName': cluster_name},
        UpdateExpression='SET IsValidate = :is_ok, NodesCount = :nodes_count',
        ExpressionAttributeValues={':is_ok': is_ok, ':nodes_count': nodes_count},
        ReturnValues='ALL_NEW'
    )

    updated_item = response.get('Attributes', {})
    print(f'Updated DynamoDB Item: {updated_item}')

def lambda_handler(event, context):
    try:
        cluster_id_mapping = {
            'cc-ndc-eks-cluster-dev-cluster': '670cd21b-4a42-11ee-9d3c-5feaf422a957',
            'cc-ndc-eks-cluster-int-cluster': '63391be1-4a42-11ee-9a0e-5feaf422a957',
            'cc-ndc-eks-cluster-staging-cluster': '63bb1ae5-4a42-11ee-8372-5feaf422a957',
            'cc-ndc-eks-cluster-test-cluster': '67eea79f-4a42-11ee-8dd3-5feaf422a957',
        }

        clusters = get_clusters()

        for cluster_name in clusters:
            cluster_endpoint = get_eks_cluster_endpoint(cluster_name)
            twistlock_running_pods = get_running_twistlock_pods(cluster_name)
            nodes_count = get_nodes_count()

            unique_id = cluster_id_mapping.get(cluster_name, '')  # Get unique ID from the mapping
            if not unique_id:
                print(f'Error: Unique ID not found for cluster {cluster_name}')
                continue

            is_ok = len(twistlock_running_pods) > 0 and len(twistlock_running_pods) == nodes_count
            assume_role_and_update_dynamodb(cluster_name, is_ok, nodes_count, unique_id)

            print(f'Cluster: {cluster_name}')
            print(f'Number of Nodes in the Cluster: {nodes_count}')
            print(f'Twistlock Pods Running: {twistlock_running_pods}')
            print("----------")

        return {
            'statusCode': 200,
            'body': json.dumps({'Message': 'Processing completed for all clusters'})
        }
    except Exception as e:
        print(f"Error in lambda_handler: {e}")
        raise

# Uncomment the line below to test the lambda locally
# lambda_handler(None, None)
