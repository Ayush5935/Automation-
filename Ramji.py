import boto3

# Source AWS account information
source_account_id = 'source_account_id'
source_region = 'us-west-2'
source_ami_id = 'ami-xxxxxxxxxxxxxxxxx'  # Replace with your source AMI ID

# Destination AWS account information
destination_account_id = 'destination_account_id'
destination_region = 'us-east-1'

def copy_ami(source_session, destination_session):
    # Create a Boto3 session using the source account credentials
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
    copied_ami_resource = destination_session.resource('ec2', region_name=destination_region).Image(copied_ami_id)
    copied_ami_resource.wait_until_exists()

    # Print details of the copied AMI
    print(f"Copied AMI ID: {copied_ami_resource.id}")
    print(f"AMI Name: {copied_ami_resource.name}")
    print(f"Snapshot ID: {copied_ami_resource.block_device_mappings[0]['Ebs']['SnapshotId']}")

def main():
    # Create Boto3 sessions for the source and destination accounts
    source_session = boto3.Session(region_name=source_region)
    destination_session = boto3.Session(region_name=destination_region)

    # Copy AMI from source account to destination account
    copy_ami(source_session, destination_session)

if __name__ == '__main__':
    main()


#-----
import boto3

# Source AWS account information
source_account_id = 'source_account_id'
source_region = 'us-west-2'
source_ami_id = 'ami-xxxxxxxxxxxxxxxxx'  # Replace with your source AMI ID

# Destination AWS account information
destination_account_id = 'destination_account_id'
destination_region = 'us-east-1'

def copy_ami():
    # Create a Boto3 session using the source account credentials
    ec2_source = boto3.client('ec2', region_name=source_region)

    # Copy the AMI and its associated snapshot
    response = ec2_source.copy_image(
        SourceImageId=source_ami_id,
        SourceRegion=source_region,
        Name='CopiedAMI',
        Encrypted=True
    )

    # Get the copied AMI ID
    copied_ami_id = response['ImageId']

    # Create a Boto3 session using the destination account credentials
    ec2_destination = boto3.resource('ec2', region_name=destination_region)

    # Get the copied AMI resource in the destination account
    copied_ami = ec2_destination.Image(copied_ami_id)

    # Wait for the AMI to be available in the destination account
    copied_ami.wait_until_exists()

    # Print details of the copied AMI
    print(f"Copied AMI ID: {copied_ami.id}")
    print(f"AMI Name: {copied_ami.name}")
    print(f"Snapshot ID: {copied_ami.block_device_mappings[0]['Ebs']['SnapshotId']}")

def main():
    # Copy AMI from source account to destination account
    copy_ami()

if __name__ == '__main__':
    main()


#_____




import boto3
import time
import botocore

# Source AWS account information
source_account_id = 'source_account_id'
source_region = 'us-west-2'
source_ami_id = 'ami-xxxxxxxxxxxxxxxxx'  # Replace with your source AMI ID

# Destination AWS account information
destination_account_id = 'destination_account_id'
destination_region = 'us-east-1'

def copy_ami():
    # Create a Boto3 session using the source account credentials
    ec2_source = boto3.client('ec2', region_name=source_region)

    # Copy the AMI and its associated snapshot
    response = ec2_source.copy_image(
        SourceImageId=source_ami_id,
        SourceRegion=source_region,
        Name='CopiedAMI',
        Encrypted=True
    )

    # Get the copied AMI ID
    copied_ami_id = response['ImageId']

    # Create a Boto3 session using the destination account credentials
    ec2_destination = boto3.resource('ec2', region_name=destination_region)

    # Get the copied AMI resource in the destination account
    copied_ami = ec2_destination.Image(copied_ami_id)

    # Wait for the AMI to be available in the destination account with retries
    max_attempts = 30  # You can adjust this based on your requirements
    attempts = 0

    while attempts < max_attempts:
        try:
            copied_ami.wait_until_exists()
            break  # Break out of the loop if the wait is successful
        except botocore.exceptions.WaiterError as e:
            # Handle the specific exception when the AMI is not found
            if "InvalidAMIID.NotFound" in str(e):
                attempts += 1
                print(f"Attempt {attempts}/{max_attempts}: Waiting for the AMI to exist...")
                time.sleep(10)  # Adjust the delay between retries as needed
            else:
                raise  # Raise other exceptions

    # Print details of the copied AMI
    print(f"Copied AMI ID: {copied_ami.id}")
    print(f"AMI Name: {copied_ami.name}")
    print(f"Snapshot ID: {copied_ami.block_device_mappings[0]['Ebs']['SnapshotId']}")

def main():
    # Copy AMI from source account to destination account
    copy_ami()

if __name__ == '__main__':
    main()


