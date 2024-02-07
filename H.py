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
      - # Push Helm chart to EC



version: 0.2

phases:
  install:
    runtime-versions:
      python: 3.8
  pre_build:
    commands:
      # Install unzip utility (if not already installed)
      - apt-get update && apt-get install -y unzip
      # Download the zip file from S3
      - aws s3 cp s3://$S3_BUCKET/$ZIP_FILE_KEY .
      # Extract the zip file
      - unzip $ZIP_FILE_KEY
      # Navigate to the directory containing the Helm chart files
      - cd twistlock-defender
      # Extract version from Chart.yaml and store it in a variable
      - VERSION=$(cat Chart.yaml | grep 'version:' | awk '{print $2}')
  build:
    commands:
      # Build Docker image with version tag
      - docker build -t $ECR_REPO_URL:$VERSION .
      # Tag Docker image with ECR repository URL and version
      - docker tag $ECR_REPO_URL:$VERSION $ECR_REPO_URL:$VERSION
      # Push Docker image to ECR
      - aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $ECR_REPO_URL
      - docker push $ECR_REPO_URL:$VERSION





version: 0.2

phases:
  pre_build:
    commands:
      # Install Helm
      - curl -fsSL -o get_helm.sh https://raw.githubusercontent.com/helm/helm/master/scripts/get-helm-3
      - chmod 700 get_helm.sh
      - ./get_helm.sh

      # Install unzip utility (if not already installed)
      - apt-get update && apt-get install -y unzip

      # Download the zip file from S3
      - aws s3 cp s3://$S3_BUCKET/$ZIP_FILE_KEY .

      # Extract the zip file
      - unzip $ZIP_FILE_KEY

      # Navigate to the directory containing the Helm chart files
      - cd twistlock-defender

      # Extract version from Chart.yaml and store it in a variable
      - VERSION=$(cat Chart.yaml | grep 'version:' | awk '{print $2}')

  build:
    commands:
      # Verify Helm version
      - helm version

      # Debug: Print the contents of Chart.yaml
      - cat Chart.yaml

      # Debug: Print the value of the $VERSION variable
      - echo "Version: $VERSION"

      # Save Helm chart to Amazon ECR
      - helm chart save . $ECR_REPO_URL:$VERSION

      # Push Helm chart to Amazon ECR
      - helm chart push $ECR_REPO_URL:$VERSION
