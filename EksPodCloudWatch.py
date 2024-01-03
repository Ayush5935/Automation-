import boto3
import json
import time
from kubernetes import client, config

def create_cloudwatch_event_rule(lambda_function_name):
    cloudwatch_events_client = boto3.client('events')

    rule_name = f'{lambda_function_name}-rule'
    schedule_expression = 'rate(15 minutes)'

    response = cloudwatch_events_client.put_rule(
        Name=rule_name,
        ScheduleExpression=schedule_expression,
        State='ENABLED'
    )

    target_arn = f'arn:aws:lambda:{response["RuleArn"].split(":")[3]}:{response["RuleArn"].split(":")[4]}:function:{lambda_function_name}'

    cloudwatch_events_client.put_targets(
        Rule=rule_name,
        Targets=[
            {
                'Id': '1',
                'Arn': target_arn
            },
        ]
    )

    return rule_name

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

        # For demonstration purposes, print the pod information
        print(json.dumps(pod_info))

        return {
            'statusCode': 200,
            'body': json.dumps(pod_info)
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': f'Error: {str(e)}'
        }

# Uncomment the next two lines if you want to create the CloudWatch Events rule during the Lambda function deployment
# lambda_function_name = 'your-lambda-function-name'
# create_cloudwatch_event_rule(lambda_function_name)
￼Enter
