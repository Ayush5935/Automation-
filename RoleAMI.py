import boto3

def assume_role(source_account_id, role_name):
    sts_client = boto3.client('sts')
    assumed_role = sts_client.assume_role(
        RoleArn=f'arn:aws:iam::{source_account_id}:role/{role_name}',
        RoleSessionName='AssumedRoleSession'
    )
    return assumed_role['Credentials']

def copy_ami(source_credentials, source_region, source_ami_id, destination_account_id, destination_region):
    source_session = boto3.Session(
        aws_access_key_id=source_credentials['AccessKeyId'],
        aws_secret_access_key=source_credentials['SecretAccessKey'],
        aws_session_token=source_credentials['SessionToken'],
        region_name=source_region
    )

    # List available AMIs in the source account
    ec2_source = source_session.client('ec2', region_name=source_region)
    available_amis = ec2_source.describe_images(ImageIds=[source_ami_id])['Images']

    if not available_amis:
        print(f"No AMI found with ID {source_ami_id} in the source account.")
        return

    # Assume role in the destination account
    destination_credentials = assume_role(destination_account_id, 'AssumeRoleInDestination')

    destination_session = boto3.Session(
        aws_access_key_id=destination_credentials['AccessKeyId'],
        aws_secret_access_key=destination_credentials['SecretAccessKey'],
        aws_session_token=destination_credentials['SessionToken'],
        region_name=destination_region
    )

    # Copy the specified AMI to the destination account
    ec2_destination = destination_session.client('ec2', region_name=destination_region)
    copied_ami = ec2_destination.copy_image(
        SourceImageId=source_ami_id,
        SourceRegion=source_region,
        Name='CopiedAMI',
        Encrypted=True
    )

    print(f"AMI Copy initiated. Copied AMI ID: {copied_ami['ImageId']}")

def main():
    source_account_id = 'YOUR_SOURCE_ACCOUNT_ID'
    source_role_name = 'AssumeRoleInSource'
    source_region = 'us-west-2'
    source_ami_id = 'ami-xxxxxxxxxxxxxxxxx'
    
    destination_account_id = 'YOUR_DESTINATION_ACCOUNT_ID'
    destination_region = 'us-east-1'

    # Assume role in the source account
    source_credentials = assume_role(source_account_id, source_role_name)

    # Copy AMI from source to destination
    copy_ami(source_credentials, source_region, source_ami_id, destination_account_id, destination_region)

if __name__ == '__main__':
    main()
