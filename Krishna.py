import argparse
import boto3
from botocore.exceptions import WaiterError

def copy_ami(source_account_id, source_region, source_ami_id, destination_account_id, destination_region):
    kms_key_id = 'arn:aws:kms:us-west-2:346687249423:key/3cd4107b-98d1-486a-972c-b4734c735a69'

    source_session = boto3.Session(region_name=source_region)
    destination_session = boto3.Session(region_name=destination_region)

    # Share the AMI with the destination account
    ec2_source = source_session.client('ec2', region_name=source_region)
    ec2_source.modify_image_attribute(
        ImageId=source_ami_id,
        Attribute='launchPermission',
        LaunchPermission={'Add': [{'UserId': destination_account_id}]}
    )

    # Copy the AMI to the destination account
    ec2_destination = destination_session.client('ec2', region_name=destination_region)
    response = ec2_destination.copy_image(
        SourceImageId=source_ami_id,
        SourceRegion=source_region,
        Name='CopiedAMI',
        Encrypted=True,
        KmsKeyId=kms_key_id
    )

    copied_ami_id = response['ImageId']
    print(f"Copying AMI {source_ami_id} to {destination_account_id}... Please wait...")

    try:
        ec2_destination.get_waiter('image_available').wait(ImageIds=[copied_ami_id])
    except WaiterError as e:
        print(f"Error waiting for copied AMI in destination account: {e}")

    # Retrieve details of the copied AMI
    copied_ami = ec2_destination.describe_images(ImageIds=[copied_ami_id])['Images'][0]

    print(f"Copied AMI ID: {copied_ami['ImageId']}")
    print(f"AMI Name: {copied_ami['Name']}")
    print(f"Snapshot ID: {copied_ami['BlockDeviceMappings'][0]['Ebs']['SnapshotId']}")
    print(f"KMS Key ID: {copied_ami['KmsKeyId']}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Copy AMI from source account to destination account.')
    parser.add_argument('--source', type=str, help='Source AWS account ID')
    parser.add_argument('--source_region', type=str, help='Source AWS region')
    parser.add_argument('--ami', type=str, help='Source AMI ID to copy')
    parser.add_argument('--target', type=str, help='Destination AWS account ID')
    parser.add_argument('--target_region', type=str, help='Destination AWS region')
    args = parser.parse_args()

    copy_ami(args.source, args.source_region, args.ami, args.target, args.target_region)
￼Enter




---------

import argparse
import boto3
from botocore.exceptions import WaiterError

def copy_ami(source_account_id, source_region, source_ami_id, destination_account_id, destination_region):
    kms_key_id = 'arn:aws:kms:us-west-2:346687249423:key/3cd4107b-98d1-486a-972c-b4734c735a69'

    # Create sessions for source and destination accounts
    source_session = boto3.Session(region_name=source_region)
    destination_session = boto3.Session(region_name=destination_region)

    # Create clients for EC2 in both source and destination accounts
    ec2_source = source_session.client('ec2', region_name=source_region)
    ec2_destination = destination_session.client('ec2', region_name=destination_region)

    # Copy the AMI to the destination account
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
        # Wait for the AMI to be available in the source account
        ec2_source.get_waiter('image_available').wait(ImageIds=[source_ami_id])
    except WaiterError as e:
        print(f"Error waiting for AMI in source account: {e}")

    try:
        # Wait for the AMI to be available in the destination account
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
    parser.add_argument('--source_account', type=str, help='Source AWS account ID')
    parser.add_argument('--source_region', type=str, help='Source AWS region')
    parser.add_argument('--source_ami', type=str, help='Source AMI ID to copy')
    parser.add_argument('--destination_account', type=str, help='Destination AWS account ID')
    parser.add_argument('--destination_region', type=str, help='Destination AWS region')
    args = parser.parse_args()

    copy_ami(
        source_account_id=args.source_account,
        source_region=args.source_region,
        source_ami_id=args.source_ami,
        destination_account_id=args.destination_account,
        destination_region=args.destination_region
    )












import argparse
import boto3
from botocore.exceptions import WaiterError

def copy_ami(source_account_id, source_region, source_ami_id, destination_account_id, destination_region):
    kms_key_id_source = 'arn:aws:kms:us-west-2:346687249423:key/3cd4107b-98d1-486a-972c-b4734c735a69'
    kms_key_id_destination = 'arn:aws:kms:us-west-2:DESTINATION_ACCOUNT_ID:key/DESTINATION_KMS_KEY_ID'

    source_session = boto3.Session(region_name=source_region)
    destination_session = boto3.Session(region_name=destination_region)

    # Copy the AMI to the source account with your KMS key
    ec2_source = source_session.client('ec2', region_name=source_region)
    response_source = ec2_source.copy_image(
        SourceImageId=source_ami_id,
        SourceRegion=source_region,
        Name='CopiedAMI_Source',
        Encrypted=True,
        KmsKeyId=kms_key_id_source
    )
    copied_ami_id_source = response_source['ImageId']
    print(f"Copying AMI {source_ami_id} to source account... Please wait...")

    try:
        ec2_source.get_waiter('image_available').wait(ImageIds=[copied_ami_id_source])
    except WaiterError as e:
        print(f"Error waiting for copied AMI in source account: {e}")

    # Share the AMI with the destination account
    ec2_source.modify_image_attribute(
        ImageId=copied_ami_id_source,
        Attribute='launchPermission',
        LaunchPermission={'Add': [{'UserId': destination_account_id}]}
    )

    print(f"Sharing AMI {copied_ami_id_source} with destination account... Please wait...")

    # Copy the AMI to the destination account with the destination KMS key
    ec2_destination = destination_session.client('ec2', region_name=destination_region)
    response_destination = ec2_destination.copy_image(
        SourceImageId=copied_ami_id_source,
        SourceRegion=source_region,
        Name='CopiedAMI_Destination',
        Encrypted=True,
        KmsKeyId=kms_key_id_destination
    )
    copied_ami_id_destination = response_destination['ImageId']

    try:
        ec2_destination.get_waiter('image_available').wait(ImageIds=[copied_ami_id_destination])
    except WaiterError as e:
        print(f"Error waiting for copied AMI in destination account: {e}")

    # Retrieve details of the copied AMI in the destination account
    copied_ami_destination = ec2_destination.describe_images(ImageIds=[copied_ami_id_destination])['Images'][0]

    print(f"Copied AMI ID in destination account: {copied_ami_destination['ImageId']}")
    print(f"AMI Name in destination account: {copied_ami_destination['Name']}")
    print(f"Snapshot ID in destination account: {copied_ami_destination['BlockDeviceMappings'][0]['Ebs']['SnapshotId']}")
    print(f"KMS Key ID in destination account: {copied_ami_destination['KmsKeyId']}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Copy AMI from source account to destination account.')
    parser.add_argument('--source', type=str, help='Source AWS account ID')
    parser.add_argument('--source_region', type=str, help='Source AWS region')
    parser.add_argument('--ami', type=str, help='Source AMI ID to copy')
    parser.add_argument('--target', type=str, help='Destination AWS account ID')
    parser.add_argument('--target_region', type=str, help='Destination AWS region')
    args = parser.parse_args()

    copy_ami(args.source, args.source_region, args.ami, args.target, args.target_region)

