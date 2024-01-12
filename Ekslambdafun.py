import boto3
import json

def invoke_codebuild_for_cluster(cluster_name):
    client = boto3.client('codebuild')

    response = client.start_build(
        projectName='your-codebuild-project-name',
        sourceVersion=cluster_name  # Pass cluster name as source version
    )

    build_id = response['build']['id']
    print(f"CodeBuild triggered for cluster {cluster_name}. Build ID: {build_id}")

def list_clusters_in_regions():
    regions = boto3.session.Session().get_available_regions('eks')

    all_clusters = []
    for region in regions:
        eks_client = boto3.client('eks', region_name=region)
        response = eks_client.list_clusters()
        clusters = response.get('clusters', [])
        all_clusters.extend(clusters)

    return all_clusters

def lambda_handler(event, context):
    try:
        clusters = list_clusters_in_regions()

        for cluster_name in clusters:
            invoke_codebuild_for_cluster(cluster_name)

        print("All Clusters processed")

        return {
            'statusCode': 200,
            'body': json.dumps({'Message': 'Cluster processing completed'}),
        }
    except Exception as e:
        print(f"Error in lambda_handler: {e}")
        raise

# Uncomment the line below if you want to test the Lambda locally
# lambda_handler(None, None)
￼Enter
