import argparse
import boto3

def copy_ami(source_account, source_region, source_ami, target_account, target_region):
    source_session = boto3.Session(region_name=source_region)
    destination_session = boto3.Session(region_name=target_region)

    # Create a Boto3 session using the source account credentials
    ec2_source = source_session.client('ec2', region_name=source_region)

    # Copy the AMI and its associated snapshot
    response = ec2_source.copy_image(
        SourceImageId=source_ami,
        SourceRegion=source_region,
        Name=f'CopiedAMI_{source_ami}',
        Encrypted=True
    )

    # Wait for the AMI copy to complete
    copied_ami_id = response['ImageId']
    waiter = ec2_source.get_waiter('image_available')
    waiter.wait(ImageIds=[copied_ami_id])

    # Create a Boto3 session using the destination account credentials
    ec2_destination = destination_session.client('ec2', region_name=target_region)

    # Describe the copied AMI in the destination account
    copied_ami = ec2_destination.describe_images(ImageIds=[copied_ami_id])['Images'][0]

    # Print details of the copied AMI
    print(f"Copied AMI ID: {copied_ami['ImageId']}")
    print(f"AMI Name: {copied_ami['Name']}")
    print(f"Snapshot ID: {copied_ami['BlockDeviceMappings'][0]['Ebs']['SnapshotId']}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Copy AMI from source account to destination account')
    parser.add_argument('--source', required=True, help='Source AWS account ID')
    parser.add_argument('--source_region', required=True, help='Source AWS region')
    parser.add_argument('--target', required=True, help='Destination AWS account ID')
    parser.add_argument('--target_region', required=True, help='Destination AWS region')
    parser.add_argument('--ami', required=True, help='Source AMI ID to be copied')

    args = parser.parse_args()

    # Copy AMI
    copy_ami(args.source, args.source_region, args.ami, args.target, args.target_region)
