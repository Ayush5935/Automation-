import argparse
import boto3
from botocore.exceptions import WaiterError

def copy_ami(source_account_id, source_region, source_ami_id, destination_account_id, destination_region):
    kms_key_id = 'arn:aws:kms:us-west-2:346687249423:key/3cd4107b-98d1-486a-972c-b4734c735a69'
    source_session = boto3.Session(region_name=source_region)
    destination_session = boto3.Session(region_name=destination_region)
    
    ec2_source = source_session.client('ec2', region_name=source_region)
    response = ec2_source.copy_image(
        SourceImageId=source_ami_id,
        SourceRegion=source_region,
        Name='CopiedAMI',
        Encrypted=True,
        KmsKeyId=kms_key_id
    )
    copied_ami_id = response['ImageId']
    print(f"Copying AMI {source_ami_id} to {destination_account_id}... Please wait...")
    
    try:
        ec2_source.get_waiter('image_available').wait(ImageIds=[source_ami_id])
    except WaiterError as e:
        print(f"Error waiting for AMI in source account: {e}")
    
    ec2_destination = destination_session.client('ec2', region_name=destination_region)
    
    try:
        waiter = ec2_destination.get_waiter('image_available')
        waiter.config.max_attempts = 180  # You may adjust this value based on your AMI creation time
        waiter.wait(ImageIds=[copied_ami_id])
    except WaiterError as e:
        print(f"Error waiting for copied AMI in destination account: {e}")
        print("Continuing with additional checks...")
    
    # Additional checks
    try:
        copied_ami = ec2_destination.describe_images(ImageIds=[copied_ami_id])['Images'][0]
        print(f"Copied AMI ID: {copied_ami['ImageId']}")
        print(f"AMI Name: {copied_ami['Name']}")
        print(f"Snapshot ID: {copied_ami['BlockDeviceMappings'][0]['Ebs']['SnapshotId']}")
    except Exception as e:
        print(f"Error describing copied AMI in destination account: {e}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Copy AMI from source account to destination account.')
    parser.add_argument('--source', type=str, help='Source AWS account ID')
    parser.add_argument('--source_region', type=str, help='Source AWS region')
    parser.add_argument('--ami', type=str, help='Source AMI ID to copy')
    parser.add_argument('--target', type=str, help='Destination AWS account ID')
    parser.add_argument('--target_region', type=str, help='Destination AWS region')
    args = parser.parse_args()
    copy_ami(args.source, args.source_region, args.ami, args.target, args.target_region)
