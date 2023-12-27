huimport argparse
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




from botocore.exceptions import WaiterError
import boto3
from time import sleep

# ... (existing code)

def assume_role(target_account_id, target_role_name):
    sts_client = boto3.client('sts')

    role_arn = f'arn:aws:iam::{target_account_id}:role/{target_role_name}'
    assumed_role = sts_client.assume_role(
        RoleArn=role_arn,
        RoleSessionName='AssumedRoleSession'
    )

    credentials = assumed_role['Credentials']
    return {
        'aws_access_key_id': credentials['AccessKeyId'],
        'aws_secret_access_key': credentials['SecretAccessKey'],
        'aws_session_token': credentials['SessionToken']
    }

def create_instance_and_ami(ec2_destination, ami, instance_name="CopiedInstance"):
    # Assume role in the target account
    assumed_role_credentials = assume_role(target_account_id, target_role_name)

    # Create an EC2 instance in the target account
    ec2_target = boto3.client('ec2', region_name=target_region, **assumed_role_credentials)
    
    response_run_instance = ec2_target.run_instances(
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

    # ... (rest of the code)




import argparse
import boto3
from botocore.exceptions import WaiterError
from time import sleep

def assume_role_and_create_instance(target_account_id, target_region, role_name, ami_id, instance_name="CopiedInstance"):
    sts_client = boto3.client('sts')
    
    # Assume role in the target account
    role_arn = f"arn:aws:iam::{target_account_id}:role/{role_name}"
    assumed_role = sts_client.assume_role(
        RoleArn=role_arn,
        RoleSessionName="AssumedRoleSession"
    )

    # Use temporary credentials to create an EC2 instance
    ec2_client = boto3.client(
        'ec2',
        region_name=target_region,
        aws_access_key_id=assumed_role['Credentials']['AccessKeyId'],
        aws_secret_access_key=assumed_role['Credentials']['SecretAccessKey'],
        aws_session_token=assumed_role['Credentials']['SessionToken']
    )

    # Rest of the code to create the EC2 instance
    response_run_instance = ec2_client.run_instances(
        ImageId=ami_id,
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
    print(f"Launched EC2 instance {instance_id} using the copied AMI in the target account.")

    # Wait for the instance to be running
    ec2_client.get_waiter('instance_running').wait(InstanceIds=[instance_id])
    print(f"EC2 instance {instance_id} is now running in the target account.")

    # Create a new AMI from the running instance
    response_create_ami = ec2_client.create_image(
        InstanceId=instance_id,
        Name=f'NewAMI_{instance_name}',
        Description=f'AMI created from instance {instance_id}',
        NoReboot=True
    )

    new_ami_id = response_create_ami['ImageId']
    print(f"Created new AMI {new_ami_id} from the running instance in the target account.")

    return instance_id, new_ami_id

def copy_ami_and_create_instance(source_account_id, source_region, source_ami_id, target_account_id, target_region, role_name):
    kms_key_id = 'arn:aws:kms:us-west-2:346687249423:key/3cd4107b-98d1-486a-972c-b4734c735a69'
    source_session = boto3.Session(region_name=source_region)
    destination_session = boto3.Session(region_name=target_region)
    ec2_source = source_session.client('ec2', region_name=source_region)

    # Copy AMI in source account
    response = ec2_source.copy_image(
        SourceImageId=source_ami_id,
        SourceRegion=source_region,
        Name='CopiedAMI',
        Encrypted=True,
        KmsKeyId=kms_key_id
    )
    copied_ami_id = response['ImageId']
    print(f"Copying AMI {source_ami_id} to source account... Please wait...")

    try:
        ec2_source.get_waiter('image_available').wait(ImageIds=[source_ami_id])
    except WaiterError as e:
        print(f"Error waiting for AMI in source account: {e}")

    ec2_destination = destination_session.client('ec2', region_name=target_region)

    # Share AMI with destination account
    response_share_ami = ec2_source.modify_image_attribute(
        ImageId=source_ami_id,
        LaunchPermission={
            'Add': [{'UserId': target_account_id}]
        }
    )

    print(f"Sharing AMI {source_ami_id} with destination account... Please wait...")

    try:
        ec2_destination.get_waiter('image_available').wait(ImageIds=[copied_ami_id])
    except WaiterError as e:
        print(f"Error waiting for copied AMI in destination account: {e}")

    # Describe the copied AMI in the destination account
    try:
        copied_ami_destination = ec2_destination.describe_images(ImageIds=[copied_ami_id])['Images'][0]
        print(f"Copied AMI ID in destination account: {copied_ami_destination['ImageId']}")
        print(f"AMI Name in destination account: {copied_ami_destination['Name']}")
        print(f"Snapshot ID in destination account: {copied_ami_destination['BlockDeviceMappings'][0]['Ebs']['SnapshotId']}")
    except Exception as e:
        print(f"Error describing copied AMI in destination account: {e}")

    # Call the function to create an instance in the target account
    assume_role_and_create_instance(target_account_id, target_region,        role_name, copied_ami_id, instance_name="CopiedInstance")

# Add this code at the end of the copy_ami function
instance_id, new_ami_id = assume_role_and_create_instance(
    target_account_id, target_region, role_name, copied_ami_id
)
print(f"Instance ID: {instance_id}")
print(f"New AMI ID created from the instance: {new_ami_id}")

# Return the copied AMI ID for potential further use
return copied_ami_id

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





import boto3
import argparse
from botocore.exceptions import WaiterError
from time import sleep, time

def sso_session():
    start_url = 'https://d-92670ca28f.awsapps.com/start#/'
    sso_oidc = boto3.client('sso-oidc', region_name="us-west-2")
    client_creds = sso_oidc.register_client(
        clientName='myapp',
        clientType='public',
    )
    device_authorization = sso_oidc.start_device_authorization(
        clientId=client_creds['clientId'],
        clientSecret=client_creds['clientSecret'],
        startUrl=start_url,
    )
    url = device_authorization['verificationUriComplete']
    device_code = device_authorization['deviceCode']
    expires_in = device_authorization['expiresIn']
    interval = device_authorization['interval']
    print(f"Please authorize the application by visiting: {url}")

    expiration_time = time() + expires_in

    while time() < expiration_time:
        try:
            token = sso_oidc.create_token(
                grantType='urn:ietf:params:oauth:grant-type:device_code',
                deviceCode=device_code,
                clientId=client_creds['clientId'],
                clientSecret=client_creds['clientSecret'],
            )
            access_token = token['accessToken']
            return access_token, sso_oidc
        except sso_oidc.exceptions.AuthorizationPendingException:
            sleep(interval)
        except Exception as e:
            print(f"An error occurred: {e}")
            exit(1)

    print("SSO session expired. Please restart the process.")
    exit(1)

def copy_ami(source, source_region, ami, target, target_region):
    access_token, sso_oidc = sso_session()

    source_session = boto3.Session(region_name=source_region)
    destination_session = boto3.Session(region_name=target_region)

    ec2_source = source_session.client('ec2', region_name=source_region)
    response_source = ec2_source.copy_image(
        SourceImageId=ami,
        SourceRegion=source_region,
        Name='CopiedAMI_Source',
        Encrypted=True,
        KmsKeyId='arn:aws:kms:us-west-2:346687249423:key/3cd4107b-98d1-486a-972c-b4734c735a69'
    )
    copied_ami_id_source = response_source['ImageId']

    print(f"Copying AMI {ami} to source account {source}... Please wait...")

    try:
        ec2_source.get_waiter('image_available').wait(ImageIds=[copied_ami_id_source])
    except WaiterError as e:
        print(f"Error waiting for copied AMI in source account: {e}")

    ec2_source.modify_image_attribute(
        ImageId=copied_ami_id_source,
        Attribute='launchPermission',
        LaunchPermission={'Add': [{'UserId': target}]}
    )

    print(f"Sharing AMI {copied_ami_id_source} with destination account {target}... Please wait...")

    ec2_destination = destination_session.client('ec2', region_name=target_region)
    copied_ami_source = ec2_source.describe_images(ImageIds=[copied_ami_id_source])['Images'][0]

    instance_id, new_ami_id = assume_role_and_create_instance(
        target, target_region, copied_ami_id_source, instance_name="CopiedInstance", access_token=access_token, sso_oidc=sso_oidc
    )

    print(f"Instance ID: {instance_id}")
    print(f"New AMI ID created from the instance {instance_id}: {new_ami_id}")

    delete_confirmation = input("Do you want to delete the copied resources? (Y/N): ").strip().lower()

    if delete_confirmation == 'y':
        ec2_target = assume_role(target, target_region, access_token=access_token, sso_oidc=sso_oidc)
        delete_resources(
            ec2_source, copied_ami_source['ImageId'],
            copied_ami_source['BlockDeviceMappings'][0]['Ebs']['SnapshotId'],
            ec2_target, new_ami_id, instance_id
        )

def assume_role(target, region, access_token=None, sso_oidc=None):
    sts_client = boto3.client('sts')
    role_arn = f"arn:aws:iam::{target}:role/ami_copy_role"

    if access_token:
        credentials = sts_client.assume_role_with_sso(
            RoleArn=role_arn,
            RoleSessionName="AssumedRoleSession",
            AccessToken=access_token
        )['Credentials']
    else:
        credentials = sts_client.assume_role(
            RoleArn=role_arn,
            RoleSessionName="AssumedRoleSession"
        )['Credentials']

    return boto3.client(
        'ec2',
        region_name=region,
        aws_access_key_id=credentials['AccessKeyId'],
        aws_secret_access_key=credentials['SecretAccessKey'],
        aws_session_token=credentials['SessionToken']
    )

def assume_role_and_create_instance(target, target_region, copied_ami_id, instance_name="CopiedInstance", access_token=None, sso_oidc=None):
    sts_client = boto3.client('sts')
    role_arn = f"arn:aws:iam::{target}:role/ami_copy_role"

    if access_token:
        credentials = sts_client.assume_role_with_sso(
            RoleArn=role_arn,
            RoleSessionName="AssumedRoleSession",
            AccessToken=access_token
        )['Credentials']
    else:
        credentials = sts_client.assume_role(
            RoleArn=role_arn,
            RoleSessionName="AssumedRoleSession"
        )['Credentials']

    ec2_client = boto3.client(
        'ec2',
        region_name=target_region,
        aws_access_key_id=credentials['AccessKeyId'],
        aws_secret_access_key=credentials['SecretAccessKey'],
        aws_session_token=credentials['SessionToken']
    )

    response_run_instance = ec2_client.run_instances(
        ImageId=copied_ami_id,
        InstanceType='t2.micro',
        MinCount=1,
        MaxCount=1,
        TagSpecifications=[{
            'ResourceType': 'instance',
            'Tags': [{'Key': 'Name', 'Value': instance_name}]
        }],
        NetworkInterfaces=[{'AssociatePublicIpAddress': False, 'DeviceIndex': 0}]
    )

    instance_id = response_run_instance['Instances'][0]['InstanceId']
    print(f"Launched EC2 instance {instance_id} using the copied AMI.")
    ec2_client.get_waiter('instance_running').wait(InstanceIds=[instance_id])
    print(f"EC2 instance {instance_id} is now running.")

    response_create_ami = ec2_client.create_image(
        InstanceId=instance_id,
        Name=f'NewAMI_{instance_name}',
        Description=f'AMI created from instance {instance_id}',
        NoReboot=True
    )

    new_ami_id = response_create_ami['ImageId']
    print(f"Created new AMI {new_ami_id} from the running instance {instance_id}.")
    ec2_client.get_waiter('image_available').wait(ImageIds=[new_ami_id])
    print(f"New AMI {new_ami_id} is now fully available.")

    return instance_id, new_ami_id

def delete_resources(ec2_source, ami_id_source, snapshot_id_source, ec2_destination, ami_id_destination, instance_id):
    ec2_source.deregister_image(ImageId=ami_id_source)
    print(f"Deleted AMI from Source Account {ami_id_source}")

    ec2_source.delete_snapshot(SnapshotId=snapshot_id_source)
    print(f"Deleted Snapshot {snapshot_id_source} of AMI {ami_id_source} from Source Account")

    ec2_destination.terminate_instances(InstanceIds=[instance_id])
    print(f"Terminated EC2 instance from Target Account {instance_id}")

    ec2_destination.deregister_image(ImageId=ami_id_destination)
    print(f"Deleted AMI from Target Account {ami_id_destination}")

    snapshot_id_destination = ec2_destination.describe_images(ImageIds=[ami_id_destination])['Images'][0]['BlockDeviceMappings'][0]['Ebs']['SnapshotId']
    ec2_destination.delete_snapshot(SnapshotId=snapshot_id_destination)
    print(f"Deleted Snapshot {snapshot_id_destination} of AMI {ami_id_destination} from Target Account")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Copy AMI from source account to destination account.')
    parser.add_argument('--source', type=str, help='Source AWS account ID')
    parser.add_argument('--source_region', type=str, help='Source AWS region')
    parser.add_argument('--ami', type=str, help='Source AMI ID to copy')
    parser.add_argument('--target', type=str, help='Destination AWS account ID')
    parser.add_argument('--target_region', type=str, help='Destination AWS region')
    args = parser.parse_args()
    copy_ami(args.source, args.source_region, args.ami, args.target, args.target_region)


