from botocore.exceptions import WaiterError
import argparse
import boto3

def copy_ami_and_create_instance(source, source_region, ami, target, target_region, role_name):
    kms_key_id = 'arn:aws:kms:us-west-2:346687249423:key/3cd4107b-98d1-486a-972c-b4734c735a69'
    source_session = boto3.Session(region_name=source_region)
    destination_session = boto3.Session(region_name=target_region)

    ec2_source = source_session.client('ec2', region_name=source_region)

    # Copying AMI to Source account
    response_source = ec2_source.copy_image(
        SourceImageId=ami,
        SourceRegion=source_region,
        Name='CopiedAMI_Source',
        Encrypted=True,
        KmsKeyId=kms_key_id
    )
    copied_ami_id_source = response_source['ImageId']
    print(f"Copying AMI {ami} to source account {source}... Please wait...")

    try:
        ec2_source.get_waiter('image_available').wait(ImageIds=[copied_ami_id_source])
    except WaiterError as e:
        print(f"Error waiting for copied AMI in source account: {e}")

    # Sharimg yo target account
    ec2_source.modify_image_attribute(
        ImageId=copied_ami_id_source,
        Attribute='launchPermission',
        LaunchPermission={'Add': [{'UserId': target}]}
    )
    print(f"Sharing AMI {copied_ami_id_source} with destination account {target}... Please wait...")
from botocore.exceptions import WaiterError
import argparse
import boto3

def copy_ami_and_create_instance(source, source_region, ami, target, target_region, role_name):
    kms_key_id = 'arn:aws:kms:us-west-2:346687249423:key/3cd4107b-98d1-486a-972c-b4734c735a69'
    source_session = boto3.Session(region_name=source_region)
    destination_session = boto3.Session(region_name=target_region)

    ec2_source = source_session.client('ec2', region_name=source_region)

    # Copying AMI to Source account
    response_source = ec2_source.copy_image(
        SourceImageId=ami,
        SourceRegion=source_region,
        Name='CopiedAMI_Source',
        Encrypted=True,
        KmsKeyId=kms_key_id
    )
    copied_ami_id_source = response_source['ImageId']
    print(f"Copying AMI {ami} to source account {source}... Please wait...")

    try:
        ec2_source.get_waiter('image_available').wait(ImageIds=[copied_ami_id_source])
    except WaiterError as e:
        print(f"Error waiting for copied AMI in source account: {e}")

    # Sharimg yo target account
    ec2_source.modify_image_attribute(
        ImageId=copied_ami_id_source,
        Attribute='launchPermission',
        LaunchPermission={'Add': [{'UserId': target}]}
    )
    print(f"Sharing AMI {copied_ami_id_source} with destination account {target}... Please wait...")

    ec2_destination = destination_session.client('ec2', region_name=target_region)
    
    copied_ami_source = ec2_source.describe_images(ImageIds=[copied_ami_id_source])['Images'][0]

    # Assume role and create an instance in the target account
    instance_id, new_ami_id = assume_role_and_create_instance(
        target, target_region, role_name, copied_ami_id_source, instance_name="CopiedInstance"
    )

    print(f"Instance ID: {instance_id}")
    print(f"New AMI ID created from the instance: {new_ami_id}")

    return copied_ami_id_source

def assume_role_and_create_instance(target_account_id, target_region, role_name, copied_ami_id, instance_name="CopiedInstance"):
    sts_client = boto3.client('sts')
    
    # Assume role in the target account
    role_arn = f"arn:aws:iam::{target_account_id}:role/{role_name}"
    assumed_role = sts_client.assume_role(
        RoleArn=role_arn,
        RoleSessionName="AssumedRoleSession"
    )
    
    # Create an EC2 instance using the copied AMI in the target account
    ec2_client = boto3.client('ec2', region_name=target_region,
                             aws_access_key_id=assumed_role['Credentials']['AccessKeyId'],
                             aws_secret_access_key=assumed_role['Credentials']['SecretAccessKey'],
                             aws_session_token=assumed_role['Credentials']['SessionToken'])

    response_run_instance = ec2_client.run_instances(
        ImageId=copied_ami_id,
        InstanceType='t2.micro',
        MinCount=1,
        MaxCount=1,
        TagSpecifications=[
            {
                'ResourceType': 'instance',
                'Tags': [
                    {'Key': 'Name', 'Value': instance_name}
                ]
            }
        ]
    )

    instance_id = response_run_instance['Instances'][0]['InstanceId']
    print(f"Launched EC2 instance {instance_id} using the copied AMI.")

    # Wait for the instance to be running
    ec2_client.get_waiter('instance_running').wait(InstanceIds=[instance_id])
    print(f"EC2 instance {instance_id} is now running.")

    # Create a new AMI from the running instance
    response_create_ami = ec2_client.create_image(
        InstanceId=instance_id,
        Name=f'NewAMI_{instance_name}',
        Description=f'AMI created from instance {instance_id}',
        NoReboot=True
    )

    new_ami_id = response_create_ami['ImageId']
    print(f"Created new AMI {new_ami_id} from the running instance {instance_id}.")

    return instance_id, new_ami_id

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Copy AMI from source account to destination account.')
    parser.add_argument('--source', type=str, help='Source AWS account ID')
    parser.add_argument('--source_region', type=str, help='Source AWS region')
    parser.add_argument('--ami', type=str, help='Source AMI ID to copy')
    parser.add_argument('--target', type=str, help='Destination AWS account ID')
    parser.add_argument('--target_region', type=str, help='Destination AWS region')
    parser.add_argument('--role_name', type=str, help='Name of the role to assume in the target account')
    args = parser.parse_args()

    copy_ami_and_create_instance(args.source, args.source_region, args.ami, args.target, args.target_region, args.role_name)






def create_instance_and_ami(ec2_destination, ami, instance_name="CopiedInstance"):
    # Creating EC2 from the AMI (source account)
    response_run_instance = ec2_destination.run_instances(
        ImageId=ami,
        InstanceType='t2.micro',
        MinCount=1,
        MaxCount=1,
        TagSpecifications=[
            {
                'ResourceType': 'instance',
                'Tags': [
                    {'Key': 'Name', 'Value': instance_name}
                ]
            }
        ],
        # Explicitly set AssociatePublicIpAddress to False
        NetworkInterfaces=[{'AssociatePublicIpAddress': False, 'DeviceIndex': 0}]
    )

    instance_id = response_run_instance['Instances'][0]['InstanceId']
    print(f"Launched EC2 instance {instance_id} using the copied AMI.")

    # Wait for the instance to be running
    ec2_destination.get_waiter('instance_running').wait(InstanceIds=[instance_id])
    print(f"EC2 instance {instance_id} is now running.")

    # Create a new AMI from the running instance
    response_create_ami = ec2_destination.create_image(
        InstanceId=instance_id,
        Name=f'NewAMI_{instance_name}',
        Description=f'AMI created from instance {instance_id}',
        NoReboot=True
    )

    new_ami_id = response_create_ami['ImageId']
    print(f"Created new AMI {new_ami_id} from the running instance {instance_id}.")

    # Wait until the new AMI is fully available
    ec2_destination.get_waiter('image_available').wait(ImageIds=[new_ami_id])
    print(f"New AMI {new_ami_id} is now fully available.")

    # Describe the new AMI
    new_ami_details = ec2_destination.describe_images(ImageIds=[new_ami_id])['Images'][0]
    print(f"Details of the new AMI {new_ami_id}: {new_ami_details}")

    return instance_id, new_ami_id, new_ami_details




import argparse
import boto3
from botocore.exceptions import WaiterError

def copy_ami(source, source_region, ami, target, target_region):
    kms_key_id = 'arn:aws:kms:us-west-2:346687249423:key/3cd4107b-98d1-486a-972c-b4734c735a69'
    source_session = boto3.Session(region_name=source_region)
    destination_session = boto3.Session(region_name=target_region)

    # Copying AMI to Source account
    ec2_source = source_session.client('ec2', region_name=source_region)
    response_source = ec2_source.copy_image(
        SourceImageId=ami,
        SourceRegion=source_region,
        Name='CopiedAMI_Source',
        Encrypted=True,
        KmsKeyId=kms_key_id
    )
    copied_ami_id_source = response_source['ImageId']
    print(f"Copying AMI {ami} to source account {source}... Please wait...")

    try:
        ec2_source.get_waiter('image_available').wait(ImageIds=[copied_ami_id_source])
    except WaiterError as e:
        print(f"Error waiting for copied AMI in source account: {e}")

    # Sharing to target account
    ec2_source.modify_image_attribute(
        ImageId=copied_ami_id_source,
        Attribute='launchPermission',
        LaunchPermission={'Add': [{'UserId': target}]}
    )
    print(f"Sharing AMI {copied_ami_id_source} with destination account {target}... Please wait...")

    # Creating an EC2 instance in the target account
    copied_ami_source = assume_role_and_create_instance(target, target_region, copied_ami_id_source, instance_name="CopiedInstance")

    # Create a new AMI from the running instance
    instance_id, new_ami_id = create_instance_and_ami(ec2_source, copied_ami_source)
    print(f"Instance ID: {instance_id}")
    print(f"New AMI ID created from the instance: {new_ami_id}")

    # Ask the user if they want to delete resources
    delete_copied_ami = input("Do you want to delete the copied AMI in the source account? (Y/N): ").strip().lower() == 'y'
    delete_instance = input("Do you want to delete the instance in the target account? (Y/N): ").strip().lower() == 'y'
    delete_new_ami = input("Do you want to delete the new AMI in the source account? (Y/N): ").strip().lower() == 'y'

    # Perform deletion based on user input
    if delete_copied_ami:
        delete_ami(ec2_source, copied_ami_id_source)
    if delete_instance:
        delete_instance_in_target(target, target_region, instance_id)
    if delete_new_ami:
        delete_ami(ec2_source, new_ami_id)

def assume_role_and_create_instance(role_arn, region, ami, instance_name="CopiedInstance"):
    # Assume role in the target account
    sts_client = boto3.client('sts')
    assumed_role = sts_client.assume_role(
        RoleArn=role_arn,
        RoleSessionName="AssumedRoleSession"
    )

    # Create an EC2 instance in the target account
    ec2_client = boto3.client('ec2', region_name=region, aws_access_key_id=assumed_role['Credentials']['AccessKeyId'],
                              aws_secret_access_key=assumed_role['Credentials']['SecretAccessKey'],
                              aws_session_token=assumed_role['Credentials']['SessionToken'])
    return create_instance_and_ami(ec2_client, ami, instance_name)

def create_instance_and_ami(ec2_client, ami, instance_name="CopiedInstance"):
    # Create an EC2 instance using the copied AMI
    response_run_instance = ec2_client.run_instances(
        ImageId=ami,
        InstanceType='t2.micro',
        MinCount=1,
        MaxCount=1,
        TagSpecifications=[
            {
                'ResourceType': 'instance',
                'Tags': [
                    {'Key': 'Name', 'Value': instance_name}
                ]
            }
        ]
    )

    instance_id = response_run_instance['Instances'][0]['InstanceId']
    print(f"Launched EC2 instance {instance_id} using the copied AMI.")

    # Wait for the instance to be running
    ec2_client.get_waiter('instance_running').wait(InstanceIds=[instance_id])
    print(f"EC2 instance {instance_id} is now running.")

    # Create a new AMI from the running instance
    response_create_ami = ec2_client.create_image(
        InstanceId=instance_id,
        Name=f'NewAMI_{instance_name}',
        Description=f'AMI created from instance {instance_id}',
        NoReboot=True
    )

    new_ami_id = response_create_ami['ImageId']
    print(f"Created new AMI {new_ami_id} from the running instance.")

    return instance_id, new_ami_id

def delete_ami(ec2_client, ami_id):
    # Deregister the AMI
    ec2_client.deregister_image(ImageId=ami_id)
    print(f"Deleted AMI {ami_id}")

def delete_instance_in_target(target, region, instance_id):
    # Assume role in the target account
    sts_client = boto3


