import os
import boto3
import json
import uuid

def assume_role_and_update_dynamodb(cluster_id, cluster_name, is_validate):
    assume_role_arn = 'arn:aws:iam::155880749572:role/5g-defender-installation-automation'
    
    sts_client = boto3.client('sts')
    assumed_role = sts_client.assume_role(
        RoleArn=assume_role_arn,
        RoleSessionName='AssumedRoleSession'
    )

    dynamodb = boto3.resource('dynamodb', 
                              aws_access_key_id=assumed_role['Credentials']['AccessKeyId'],
                              aws_secret_access_key=assumed_role['Credentials']['SecretAccessKey'],
                              aws_session_token=assumed_role['Credentials']['SessionToken'])

    table_name = 'twistlock-defender-cluster-version'
    table = dynamodb.Table(table_name)

    unique_id = cluster_id
    print(f'Updating DynamoDb item with id {unique_id} and eksclustername {cluster_name}')
    
    response = table.update_item(
        Key={'id': unique_id, 'eksClusterName': cluster_name},
        UpdateExpression='SET IsValidate = :val',
        ExpressionAttributeValues={':val': is_validate},
        ReturnValues='ALL_NEW'
    )

    updated_item = response.get('Attributes', {})
    print(f'Updated DynamoDB Item: {updated_item}')

def lambda_handler(event, context):
    try:
        # Cluster IDs and Names
        cluster_data = [
            {"id": "670cd21b-4a42-11ee-9d3c-5feaf422a957", "name": "cc-ndc-eks-cluster-dev-cluster"},
            {"id": "63391be1-4a42-11ee-9a0e-5feaf422a957", "name": "cc-ndc-eks-cluster-int-cluster"},
            {"id": "63bb1ae5-4a42-11ee-8372-5feaf422a957", "name": "cc-ndc-eks-cluster-staging-cluster"},
            {"id": "67eea79f-4a42-11ee-8dd3-5feaf422a957", "name": "cc-ndc-eks-cluster-test-cluster"}
        ]

        for cluster in cluster_data:
            # Assuming some condition to determine is_validate status
            is_validate = True  # Modify this based on your condition
            
            assume_role_and_update_dynamodb(cluster["id"], cluster["name"], is_validate)

        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Clusters updated successfully'})
        }
    except Exception as e:
        print(f"Error in lambda_handler: {e}")
        raise

# Uncomment the line below to test the lambda locally
# lambda_handler(None, None)
