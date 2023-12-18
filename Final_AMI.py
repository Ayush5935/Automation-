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

    # Wait for the AMI copy to complete in the source account
    copied_ami_id = response['ImageId']
    print(f"Copying AMI {source_ami_id} to {destination_account_id}... Please wait...")

    # Use a waiter to wait for the AMI to be available in the source account
    try:
        ec2_source.get_waiter('image_available').wait(ImageIds=[source_ami_id])
    except WaiterError as e:
        print(f"Error waiting for AMI in source account: {e}")
        return

    # Create a Boto3 client for EC2 in the destination region
    ec2_destination = destination_session.client('ec2', region_name=destination_region)

    # Use a waiter to wait for the AMI to be available in the destination account
    try:
        ec2_destination.get_waiter('image_available').wait(ImageIds=[copied_ami_id])
    except WaiterError as e:
        print(f"Error waiting for copied AMI in destination account: {e}")
        return

    # Describe the copied AMI in the destination account
    copied_ami = ec2_destination.describe_images(ImageIds=[copied_ami_id])['Images'][0]

    # Wait until the status of the copied AMI is 'available'
    while copied_ami['State'] != 'available':
        print("Waiting for the copied AMI to be available in the destination account...")
        try:
            ec2_destination.get_waiter('image_available').wait(ImageIds=[copied_ami_id])
        except WaiterError as e:
            print(f"Error waiting for copied AMI in destination account: {e}")
            return
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



import argparse
import boto3
from botocore.exceptions import WaiterError

def role_arn_to_session(**args):
    client = boto3.client('sts')
    response = client.assume_role(**args)
    return boto3.Session(
        aws_access_key_id=response['Credentials']['AccessKeyId'],
        aws_secret_access_key=response['Credentials']['SecretAccessKey'],
        aws_session_token=response['Credentials']['SessionToken'])

def copy_ami(source_account_id, source_region, source_ami_id, destination_account_id, destination_region):
    source_session = boto3.Session(region_name=source_region)
    destination_session = role_arn_to_session(
        RoleArn=f'arn:aws:iam::{destination_account_id}:role/DestinationRole',
        RoleSessionName='copy-ami-session'
    )

    ec2_source = source_session.client('ec2', region_name=source_region)

    response = ec2_source.copy_image(
        SourceImageId=source_ami_id,
        SourceRegion=source_region,
        Name='CopiedAMI',
        Encrypted=True
    )

    copied_ami_id = response['ImageId']

    ec2_destination = destination_session.client('ec2', region_name=destination_region)

    try:
        ec2_destination.get_waiter('image_available').wait(ImageIds=[copied_ami_id])
    except WaiterError as e:
        print(f"Error waiting for copied AMI in destination account: {e}")
        return

    copied_ami = ec2_destination.describe_images(ImageIds=[copied_ami_id])['Images'][0]

    print(f"Copied AMI ID: {copied_ami['ImageId']}")
    print(f"AMI Name: {copied_ami['Name']}")
    print(f"Snapshot ID: {copied_ami['BlockDeviceMappings'][0]['Ebs']['SnapshotId']}")

    source_snapshot = boto3.resource('ec2', region_name=source_region).Snapshot(
        copied_ami['BlockDeviceMappings'][0]['Ebs']['SnapshotId'])

    source_sharing = source_snapshot.describe_attribute(Attribute='createVolumePermission')
    if source_sharing['CreateVolumePermissions'] \
            and source_sharing['CreateVolumePermissions'][0]['UserId'] != destination_account_id:
        print("Snapshot already shared with account, creating a copy")
    else:
        print("Sharing with target account")
        source_snapshot.modify_attribute(
            Attribute='createVolumePermission',
            OperationType='add',
            UserIds=[destination_account_id]
        )

    shared_snapshot = boto3.resource('ec2', region_name=destination_region).Snapshot(
        copied_ami['BlockDeviceMappings'][0]['Ebs']['SnapshotId'])

    if shared_snapshot.state != "completed":
        print("Shared snapshot not in completed state, got: " + shared_snapshot.state)
        return

    copy = shared_snapshot.copy(
        SourceRegion=source_region,
        Encrypted=True,
    )

    copied_snapshot = boto3.resource('ec2', region_name=destination_region).Snapshot(copy['SnapshotId'])
    copied_snapshot.wait_until_completed()

    print("Created target-owned copy of shared snapshot with id: " + copy['SnapshotId'])

    new_image = boto3.resource('ec2', region_name=destination_region).register_image(
        Name='copy-' + copied_snapshot.snapshot_id,
        Architecture='x86_64',
        RootDeviceName='/dev/sda1',
        BlockDeviceMappings=[
            {
                "DeviceName": "/dev/sda1",
                "Ebs": {
                    "SnapshotId": copied_snapshot.snapshot_id,
                    "VolumeSize": copied_snapshot.volume_size,
                    "DeleteOnTermination": True,
                    "VolumeType": "gp2"
                },
            }
        ],
        VirtualizationType='hvm'
    )

    print("New AMI created: " + new_image)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Copy AMI from source account to destination account.')
    parser.add_argument('--source', type=str, help='Source AWS account ID')
    parser.add_argument('--source_region', type=str, help='Source AWS region')
    parser.add_argument('--ami', type=str, help='Source AMI ID to copy')
    parser.add_argument('--target', type=str, help='Destination AWS account ID')
    parser.add_argument('--target_region', type=str, help='Destination AWS region')
    args = parser.parse_args()

    copy_ami(args.source, args.source_region, args.ami, args.target, args.target_region)




import argparse
import boto3
from botocore.exceptions import WaiterError
from time import sleep

def copy_ami(source_account_id, source_region, source_ami_id, destination_account_id, destination_region):
    kms_key_id = 'arn:aws:kms:us-west-2:346687249423:key/3cd4107b-98d1-486a-972c-b4734c735a69'
    
    # Create sessions for both source and destination
    source_session = boto3.Session(region_name=source_region)
    destination_session = boto3.Session(region_name=destination_region)

    # Use clients for EC2 in both source and destination regions
    ec2_source = source_session.client('ec2', region_name=source_region)
    ec2_destination = destination_session.client('ec2', region_name=destination_region)

    # Copy the AMI from source to destination
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
        # Wait for the source AMI to be available
        ec2_source.get_waiter('image_available').wait(ImageIds=[source_ami_id])
    except WaiterError as e:
        print(f"Error waiting for AMI in source account: {e}")

    try:
        # Wait for the copied AMI to be available in the destination account
        ec2_destination.get_waiter('image_available').wait(ImageIds=[copied_ami_id])
    except WaiterError as e:
        print(f"Error waiting for copied AMI in destination account: {e}")

    # Describe the copied AMI in the destination account
    copied_ami = ec2_destination.describe_images(ImageIds=[copied_ami_id])['Images'][0]

    print(f"Copied AMI ID: {copied_ami['ImageId']}")
    print(f"AMI Name: {copied_ami['Name']}")
    print(f"Snapshot ID: {copied_ami['BlockDeviceMappings'][0]['Ebs']['SnapshotId']}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Copy AMI from source account to destination account.')
    parser.add_argument('--source', type=str, help='Source AWS account ID')
    parser.add_argument('--source_region', type=str, help='Source AWS region')
    parser.add_argument('--ami', type=str, help='Source AMI ID to copy')
    parser.add_argument('--target', type=str, help='Destination AWS account ID')
    parser.add_argument('--target_region', type=str, help='Destination AWS region')
    args = parser.parse_args()
    copy_ami(args.source, args.source_region, args.ami, args.target, args.target_region)




