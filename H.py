import boto3

def lambda_handler(event, context):
    # Extract bucket and key from S3 event
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']
    
    # Start CodeBuild project
    codebuild_client = boto3.client('codebuild')
    response = codebuild_client.start_build(
        projectName='your-codebuild-project-name',
        environmentVariablesOverride=[
            {
                'name': 'S3_BUCKET',
                'value': bucket
            },
            {
                'name': 'ZIP_FILE_KEY',
                'value': key
            }
        ]
    )
    print(response)




version: 0.2

phases:
  install:
    runtime-versions:
      python: 3.8
  build:
    commands:
      - aws s3 cp s3://$S3_BUCKET/$ZIP_FILE_KEY .
      - unzip $ZIP_FILE_KEY
      - # Extract Helm chart or perform other necessary steps
      - # Push Helm chart to ECR

