import boto3
import time

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

    # Polling mechanism to check the status of the AMI in the destination account
    while True:
        try:
            # Create a Boto3 session using the destination account credentials
            ec2_destination = boto3.client('ec2', region_name=destination_region)

            # Describe the copied AMI in the destination account
            copied_ami_info = ec2_destination.describe_images(ImageIds=[copied_ami_id])['Images'][0]

            # If the AMI is available, print its details and break out of the loop
            if copied_ami_info['State'] == 'available':
                print(f"Copied AMI ID: {copied_ami_info['ImageId']}")
                print(f"AMI Name: {copied_ami_info['Name']}")
                print(f"Snapshot ID: {copied_ami_info['BlockDeviceMappings'][0]['Ebs']['SnapshotId']}")
                break
        except Exception as e:
            print(f"Error: {e}")

        # If the AMI is not yet available, wait for a moment before checking again
        time.sleep(10)

def main():
    # Copy AMI from source account to destination account
    copy_ami()

if __name__ == '__main__':
    main()




import boto3
import time

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
    print(f"Copied AMI ID: {copied_ami_id}")

    # Polling mechanism to check the status of the AMI in the destination account
    while True:
        try:
            # Create a Boto3 session using the destination account credentials
            ec2_destination = boto3.client('ec2', region_name=destination_region)

            # Describe the copied AMI in the destination account
            copied_ami_info = ec2_destination.describe_images(ImageIds=[copied_ami_id])['Images'][0]

            # Print the state of the AMI
            print(f"AMI State: {copied_ami_info['State']}")

            # If the AMI is available, print its details and break out of the loop
            if copied_ami_info['State'] == 'available':
                print(f"Copied AMI ID: {copied_ami_info['ImageId']}")
                print(f"AMI Name: {copied_ami_info['Name']}")
                print(f"Snapshot ID: {copied_ami_info['BlockDeviceMappings'][0]['Ebs']['SnapshotId']}")
                break
        except Exception as e:
            print(f"Error: {e}")

        # If the AMI is not yet available, wait for a moment before checking again
        time.sleep(10)

def main():
    # Copy AMI from source account to destination account
    copy_ami()

if __name__ == '__main__':
    main()


----

import boto3
import time

# Destination AWS account information
destination_account_id = 'destination_account_id'
destination_region = 'us-east-1'
copied_ami_id = 'ami-02a93aab9d6557121'  # Replace with your copied AMI ID

def check_ami_status():
    ec2_destination = boto3.client('ec2', region_name=destination_region)

    max_attempts = 30
    attempts = 0

    while attempts < max_attempts:
        try:
            # Describe the copied AMI in the destination account
            copied_ami_info = ec2_destination.describe_images(ImageIds=[copied_ami_id])

            # Print additional details about the AMI
            print(f"Attempt {attempts + 1}/{max_attempts}")
            print(f"AMI Info: {copied_ami_info}")

            # If the AMI is available, break out of the loop
            if copied_ami_info['Images'][0]['State'] == 'available':
                print(f"Copied AMI ID: {copied_ami_info['Images'][0]['ImageId']}")
                print(f"AMI Name: {copied_ami_info['Images'][0]['Name']}")
                print(f"Snapshot ID: {copied_ami_info['Images'][0]['BlockDeviceMappings'][0]['Ebs']['SnapshotId']}")
                break
        except Exception as e:
            print(f"Error: {e}")

        # If the AMI is not yet available, wait for a moment before checking again
        time.sleep(10)
        attempts += 1

def main():
    # Check the status of the copied AMI in the destination account
    check_ami_status()

if __name__ == '__main__':
    main()







_------+

import boto3
import time

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
    print(f"Copied AMI ID: {copied_ami_id}")

    # Wait for a longer duration before checking the status
    time.sleep(120)  # Adjust the delay as needed

    # Polling mechanism to check the status of the AMI in the destination account
    while True:
        try:
            # Create a Boto3 session using the destination account credentials
            ec2_destination = boto3.client('ec2', region_name=destination_region)

            # Describe the copied AMI in the destination account
            copied_ami_info = ec2_destination.describe_images(ImageIds=[copied_ami_id])['Images'][0]

            # Print the state of the AMI
            print(f"AMI State: {copied_ami_info['State']}")

            # If the AMI is available, print its details and break out of the loop
            if copied_ami_info['State'] == 'available':
                print(f"Copied AMI ID: {copied_ami_info['ImageId']}")
                print(f"AMI Name: {copied_ami_info['Name']}")
                print(f"Snapshot ID: {copied_ami_info['BlockDeviceMappings'][0]['Ebs']['SnapshotId']}")
                break
        except Exception as e:
            print(f"Error: {e}")

        # If the AMI is not yet available, wait for a moment before checking again
        time.sleep(10)

def main():
    # Copy AMI from source account to destination account
    copy_ami()

if __name__ == '__main__':
    main()



_____

import boto3
import time

# Destination AWS account information
destination_account_id = 'destination_account_id'
destination_region = 'us-east-1'
copied_ami_id = 'ami-02a93aab9d6557121'  # Replace with your copied AMI ID

def check_ami_status():
    ec2_destination = boto3.client('ec2', region_name=destination_region)

    max_attempts = 30
    attempts = 0

    while attempts < max_attempts:
        try:
            # Describe the copied AMI in the destination account
            copied_ami_info = ec2_destination.describe_images(ImageIds=[copied_ami_id])

            # Print additional details about the AMI
            print(f"Attempt {attempts + 1}/{max_attempts}")
            print(f"AMI Info: {copied_ami_info}")

            # If the AMI is available, break out of the loop
            if copied_ami_info['Images'][0]['State'] == 'available':
                print(f"Copied AMI ID: {copied_ami_info['Images'][0]['ImageId']}")
                print(f"AMI Name: {copied_ami_info['Images'][0]['Name']}")
                print(f"Snapshot ID: {copied_ami_info['Images'][0]['BlockDeviceMappings'][0]['Ebs']['SnapshotId']}")
                break
        except Exception as e:
            print(f"Error: {e}")

        # If the AMI is not yet available, wait for a moment before checking again
        time.sleep(10)
        attempts += 1

def main():
    # Check the status of the copied AMI in the destination account
    check_ami_status()

if __name__ == '__main__':
    main()


