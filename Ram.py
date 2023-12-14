import boto3
import time

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
    ec2_source.get_waiter('image_available').wait(ImageIds=[copied_ami_id])

    # Create a Boto3 session using the destination account credentials
    ec2_destination = destination_session.client('ec2', region_name=destination_region)

    # Wait for the copied AMI to be available in the destination account
    while True:
        try:
            # Try to describe the copied AMI in the destination account
            copied_ami = ec2_destination.describe_images(ImageIds=[copied_ami_id])['Images'][0]
            break  # Break out of the loop if the describe_images call is successful
        except ec2_destination.exceptions.ClientError as e:
            # If the AMI is not found, wait for a moment and try again
            if e.response['Error']['Code'] == 'InvalidAMIID.NotFound':
                time.sleep(10)
            else:
                raise  # Raise the exception if it's not due to AMI not found

    # Print details of the copied AMI
    print(f"Copied AMI ID: {copied_ami['ImageId']}")
    print(f"AMI Name: {copied_ami['Name']}")
    print(f"Snapshot ID: {copied_ami['BlockDeviceMappings'][0]['Ebs']['SnapshotId']}")

def main():
    # Create Boto3 sessions for the source and destination accounts
    source_session = boto3.Session(region_name=source_region)
    destination_session = boto3.Session(region_name=destination_region)

    # Copy AMI from source account to destination account
    copy_ami(source_session, destination_session)

if __name__ == '__main__':
    main()
￼Enter
