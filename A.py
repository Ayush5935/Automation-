import boto3
import time

def copy_ami(source_ami_id, source_region, destination_account_id, destination_region):
    # Create EC2 clients for source and destination accounts
    ec2_source = boto3.client('ec2', region_name=source_region)
    ec2_destination = boto3.client('ec2', region_name=destination_region)

    try:
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

        wait_for_ami(ec2_destination, copied_ami_id)

        # Describe the copied AMI in the destination account
        copied_ami = ec2_destination.describe_images(ImageIds=[copied_ami_id])['Images'][0]

        # Print details of the copied AMI
        print(f"Copied AMI ID: {copied_ami['ImageId']}")
        print(f"AMI Name: {copied_ami['Name']}")
        print(f"Snapshot ID: {copied_ami['BlockDeviceMappings'][0]['Ebs']['SnapshotId']}")

    except Exception as e:
        print(f"Error: {e}")

def wait_for_ami(ec2_client, ami_id):
    max_attempts = 30
    attempts = 0

    while attempts < max_attempts:
        try:
            # Describe the copied AMI
            copied_ami_info = ec2_client.describe_images(ImageIds=[ami_id])

            # If the AMI is available, break out of the loop
            if copied_ami_info['Images'][0]['State'] == 'available':
                print(f"Copied AMI is available!")
                break
        except Exception as e:
            print(f"Error: {e}")

        # If the AMI is not yet available, wait for a moment before checking again
        time.sleep(10)
        attempts += 1

if __name__ == '__main__':
    # Replace these values with your specific details
    source_ami_id = 'ami-02224b4aaa93dae1b'
    source_region = 'us-west-2'
    
    destination_account_id = '159393304364'
    destination_region = 'us-east-1'

    copy_ami(source_ami_id, source_region, destination_account_id, destination_region)
