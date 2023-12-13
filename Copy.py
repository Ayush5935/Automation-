import boto3

def copy_ami(source_account_id, source_region, source_ami_id, dest_account_id, dest_region, dest_kms_key_id):
    # Assume role in source account
    sts_source = boto3.client('sts')
    source_credentials = sts_source.assume_role(
        RoleArn=f'arn:aws:iam::{source_account_id}:role/CrossAccountRole',
        RoleSessionName="RoleSession1"
    )['Credentials']

    # Assume role in destination account
    sts_dest = boto3.client('sts')
    dest_credentials = sts_dest.assume_role(
        RoleArn=f'arn:aws:iam::{dest_account_id}:role/CrossAccountRole',
        RoleSessionName="RoleSession1"
    )['Credentials']

    # Create EC2 clients using assumed roles
    ec2_source = boto3.client('ec2', region_name=source_region,
                              aws_access_key_id=source_credentials['AccessKeyId'],
                              aws_secret_access_key=source_credentials['SecretAccessKey'],
                              aws_session_token=source_credentials['SessionToken'])

    ec2_dest = boto3.client('ec2', region_name=dest_region,
                             aws_access_key_id=dest_credentials['AccessKeyId'],
                             aws_secret_access_key=dest_credentials['SecretAccessKey'],
                             aws_session_token=dest_credentials['SessionToken'])

    # Copy the source AMI to destination region
    copy_response = ec2_dest.copy_image(
        Name=f"Copied AMI from {source_region} - {source_ami_id}",
        SourceImageId=source_ami_id,
        SourceRegion=source_region,
        Encrypted=True,
        KmsKeyId=dest_kms_key_id
    )

    # Extract the new AMI ID in the destination region
    dest_ami_id = copy_response['ImageId']
    print(f"AMI copied to {dest_region}. New AMI ID: {dest_ami_id}")

if __name__ == '__main__':
    source_account_id = '111111111111'  # Replace with source AWS account ID
    source_region = 'us-west-1'         # Replace with source region
    source_ami_id = 'ami-xxxxxxxxxxxxxxxxx'  # Replace with source AMI ID

    dest_account_id = '222222222222'    # Replace with destination AWS account ID
    dest_region = 'us-east-1'           # Replace with destination region
    dest_kms_key_id = 'arn:aws:kms:us-east-1:222222222222:key/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx'  # Replace with destination KMS Key ID

    copy_ami(source_account_id, source_region, source_ami_id, dest_account_id, dest_region, dest_kms_key_id)
￼Enter
