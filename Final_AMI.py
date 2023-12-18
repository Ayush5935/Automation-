import boto3
import argparse
import json

def copy_ami(source_account_id, source_region, source_ami_id, target_account_id, target_region):
    # Assuming you have already set up your shared KMS key
    kms_key_id = 'arn:aws:kms:shared-region:shared-account-id:key/shared-kms-key-id'

    source_session = boto3.Session(region_name=source_region)
    ec2_source = source_session.client('ec2')

    # Copy the AMI using the shared KMS key
    response = ec2_source.copy_image(
        SourceImageId=source_ami_id,
        SourceRegion=source_region,
        Name='CopiedAMI',
        Encrypted=True,
        KmsKeyId=kms_key_id
    )

    # Wait for the AMI copy to complete
    copied_ami_id = response['ImageId']
    ec2_source.get_waiter('image_available').wait(ImageIds=[copied_ami_id])

    # Create a Boto3 session using the destination account credentials
    target_session = boto3.Session(region_name=target_region)
    ec2_destination = target_session.client('ec2')

    # Describe the copied AMI in the destination account
    copied_ami = ec2_destination.describe_images(ImageIds=[copied_ami_id])['Images'][0]

    # Print details of the copied AMI
    print(f"Copied AMI ID: {copied_ami['ImageId']}")
    print(f"AMI Name: {copied_ami['Name']}")
    print(f"Snapshot ID: {copied_ami['BlockDeviceMappings'][0]['Ebs']['SnapshotId']}")

    # Print additional details or save them as needed
    # ...

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Copy AMI from source account to destination account.')
    parser.add_argument('--source', required=True, help='Source account ID')
    parser.add_argument('--source_region', required=True, help='Source region')
    parser.add_argument('--ami', required=True, help='Source AMI ID')
    parser.add_argument('--target', required=True, help='Destination account ID')
    parser.add_argument('--target_region', required=True, help='Destination region')

    args = parser.parse_args()
    
    copy_ami(args.source, args.source_region, args.ami, args.target, args.target_region)





import argparse
import boto3
from botocore.exceptions import WaiterError

def copy_ami(source_account_id, source_region, source_ami_id, destination_account_id, destination_region):
    # Create Boto3 sessions for the source and destination accounts
    source_session = boto3.Session(region_name=source_region)
    destination_session = boto3.Session(region_name=destination_region)

    # Create a Boto3 client for EC2 in the source region
    ec2_source = source_session.client('ec2', region_name=source_region)

    # Copy the AMI and its associated snapshot
    response = ec2_source.copy_image(
        SourceImageId=source_ami_id,
        SourceRegion=source_region,
        Name='CopiedAMI',
        Encrypted=True
    )

    # Wait for the AMI copy to complete
    copied_ami_id = response['ImageId']
    print(f"Copying AMI {source_ami_id} to {destination_account_id}... Please wait...")

    # Use a waiter to wait for the AMI to be available in the source account
    try:
        ec2_source.get_waiter('image_available').wait(ImageIds=[source_ami_id])
    except WaiterError as e:
        print(f"Error waiting for AMI in source account: {e}")

    # Create a Boto3 client for EC2 in the destination region
    ec2_destination = destination_session.client('ec2', region_name=destination_region)

    # Use a waiter to wait for the AMI to be available in the destination account
    try:
        ec2_destination.get_waiter('image_available').wait(ImageIds=[copied_ami_id])
    except WaiterError as e:
        print(f"Error waiting for copied AMI in destination account: {e}")

    # Describe the copied AMI in the destination account
    copied_ami = ec2_destination.describe_images(ImageIds=[copied_ami_id])['Images'][0]

    # Print details of the copied AMI
    print(f"Copied AMI ID: {copied_ami['ImageId']}")
    print(f"AMI Name: {copied_ami['Name']}")
    print(f"Snapshot ID: {copied_ami['BlockDeviceMappings'][0]['Ebs']['SnapshotId']}")

if __name__ == '__main__':
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description='Copy AMI from source account to destination account.')
    parser.add_argument('--source', type=str, help='Source AWS account ID')
    parser.add_argument('--source_region', type=str, help='Source AWS region')
    parser.add_argument('--ami', type=str, help='Source AMI ID to copy')
    parser.add_argument('--target', type=str, help='Destination AWS account ID')
    parser.add_argument('--target_region', type=str, help='Destination AWS region')
    args = parser.parse_args()

    # Copy AMI from source account to destination account
    copy_ami(args.source, args.source_region, args.ami, args.target, args.target_region)

