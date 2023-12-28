import boto3
import argparse
from botocore.exceptions import WaiterError
from aws_requests_auth.boto_utils import BotoAWSRequestsAuth
from time import sleep
from boto3.session import Session
import webbrowser

region = 'us-west-2'

def sso_session():
    session = Session()
    start_url = 'https://d-92670ca28f.awsapps.com/start#/'
    sso_oidc = session.client('sso-oidc', region_name="us-west-2")
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
    webbrowser.open(url, autoraise=True)
    for n in range(1, expires_in // interval + 1):
        sleep(interval)
        try:
            token = sso_oidc.create_token(
                grantType='urn:ietf:params:oauth:grant-type:device_code',
                deviceCode=device_code,
                clientId=client_creds['clientId'],
                clientSecret=client_creds['clientSecret'],
            )
            break
        except sso_oidc.exceptions.AuthorizationPendingException:
            pass

    access_token = token['accessToken']
    return access_token, session

def assume_role_with_sso(target, region, sso_access_token, sso_session):
    sts_client = sso_session.client('sts')
    role_arn = f"arn:aws:iam::{target}:role/ami_copy_role"
    
    assumed_role = sts_client.assume_role_with_web_identity(
        RoleArn=role_arn,
        RoleSessionName="AssumedRoleSession",
        WebIdentityToken=sso_access_token
    )
    
    return boto3.client(
        'ec2',
        region_name=region,
        aws_access_key_id=assumed_role['Credentials']['AccessKeyId'],
        aws_secret_access_key=assumed_role['Credentials']['SecretAccessKey'],
        aws_session_token=assumed_role['Credentials']['SessionToken']
    )

def copy_ami(source, source_region, ami, target, target_region, sso_access_token, sso_session):
    kms_key_id = 'arn:aws:kms:us-west-2:346687249423:key/3cd4107b-98d1-486a-972c-b4734c735a69'

    ec2_source = assume_role_with_sso(source, source_region, sso_access_token, sso_session)

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

    # Sharing to target account
    ec2_source.modify_image_attribute(
        ImageId=copied_ami_id_source,
        Attribute='launchPermission',
        LaunchPermission={'Add': [{'UserId': target}]}
    )

    print(f"Sharing AMI {copied_ami_id_source} with destination account {target}... Please wait...")

    ec2_destination = assume_role_with_sso(target, target_region, sso_access_token, sso_session)
    copied_ami_source = ec2_source.describe_images(ImageIds=[copied_ami_id_source])['Images'][0]

    instance_id, new_ami_id = assume_role_and_create_instance(target, target_region, copied_ami_id_source, instance_name="CopiedInstance")

    print(f"Instance ID: {instance_id}")
    print(f"New AMI ID created from the instance {instance_id}: {new_ami_id}")

    delete_confirmation = input("Do you want to delete the copied resources? (Y/N): ").strip().lower()
    if delete_confirmation == 'y':
        ec2_target = assume_role_with_sso(target, target_region, sso_access_token, sso_session)
        delete_resources(ec2_source, copied_ami_source['ImageId'],
                         copied_ami_source['BlockDeviceMappings'][0]['Ebs']['SnapshotId'],
                         ec2_target, new_ami_id, instance_id)

def assume_role_with_sso(target, region, sso_access_token, sso_session):
    sts_client = sso_session.client('sts')
    role_arn = f"arn:aws:iam::{target}:role/ami_copy_role"
    
    assumed_role = sts_client.assume_role_with_web_identity(
        RoleArn=role_arn,
        RoleSessionName="AssumedRoleSession",
        WebIdentityToken=sso_access_token
    )
    
    return boto3.client(
        'ec2',
        region_name=region,
        aws_access_key_id=assumed_role['Credentials']['AccessKeyId'],
        aws_secret_access_key=assumed_role['Credentials']['SecretAccessKey'],
        aws_session_token=assumed_role['Credentials']['SessionToken']
    )

def assume_role_and_create_instance(target, target_region, copied_ami_id, instance_name="CopiedInstance"):
    sts_client = boto3.client('sts')
    role_arn = f"arn:aws:iam::{target}:role/ami_copy_role"
    assumed_role = sts_client.assume_role(
        RoleArn=role_arn,
        RoleSessionName="AssumedRoleSession"
    )
    
    ec2_client = boto3.client(
        'ec2',
        region_name=target_region,
        aws_access_key_id=assumed_role['Credentials']['AccessKeyId'],
        aws_secret_access_key=assumed_role['Credentials']['SecretAccessKey'],
        aws_session_token=assumed_role['Credentials']['SessionToken']
    )
    
    response_run_instance = ec2_client.run_instances(
        ImageId=copied_ami_id,
        InstanceType='t2.micro',
        MinCount=1,
        MaxCount=1,
        TagSpecifications=[
            {
                'ResourceType': 'instance',
                'Tags': [{'Key': 'Name', 'Value': instance_name}]
            }
        ],
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

# Entry point of the script
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Copy AMI from source account to destination account.')
    parser.add_argument('--source', type=str, help='Source AWS account ID')
    parser.add_argument('--source_region', type=str, help='Source AWS region')
    parser.add_argument('--ami', type=str, help='Source AMI ID to copy')
    parser.add_argument('--target', type=str, help='Destination AWS account ID')
    parser.add_argument('--target_region', type=str, help='Destination AWS region')
    args = parser.parse_args()

    # Call the function to get and use AWS SSO credentials
    sso_access_token, sso_session_obj = sso_session()

    # Use the obtained SSO credentials to copy the AMI between accounts
    copy_ami(args.source, args.source_region, args.ami, args.target, args.target_region, sso_access_token, sso_session_obj)

import boto3
import argparse
from botocore.exceptions import WaiterError
from aws_requests_auth.boto_utils import BotoAWSRequestsAuth
from time import sleep
import requests

region = 'us-west-2'

def sso_session():
    session = boto3.Session()
    start_url = 'https://d-92670ca28f.awsapps.com/start#/'
    sso_oidc = session.client('sso-oidc', region_name="us-west-2")
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

    print(f"Open the following URL in your browser to authenticate: {url}")
    print(f"Waiting for authentication...")

    for n in range(1, expires_in // interval + 1):
        sleep(interval)
        try:
            token_response = requests.post(
                "https://d-92670ca28f.awsapps.com/token",
                data={
                    'grant_type': 'urn:ietf:params:oauth:grant-type:device_code',
                    'device_code': device_code,
                    'client_id': client_creds['clientId'],
                    'client_secret': client_creds['clientSecret'],
                }
            )
            token_response.raise_for_status()
            token = token_response.json()
            access_token = token['access_token']
            break
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 400 and 'authorization_pending' in e.response.text:
                pass
            else:
                raise

    print("Authentication successful!")
    return access_token, session

def assume_role_with_sso(target, region, sso_access_token, sso_session):
    sts_client = sso_session.client('sts')
    role_arn = f"arn:aws:iam::{target}:role/ami_copy_role"
    
    try:
        assumed_role = sts_client.assume_role_with_web_identity(
            RoleArn=role_arn,
            RoleSessionName="AssumedRoleSession",
            WebIdentityToken=sso_access_token
        )
        
        return boto3.client(
            'ec2',
            region_name=region,
            aws_access_key_id=assumed_role['Credentials']['AccessKeyId'],
            aws_secret_access_key=assumed_role['Credentials']['SecretAccessKey'],
            aws_session_token=assumed_role['Credentials']['SessionToken']
        )
    except sts_client.exceptions.InvalidIdentityTokenException as e:
        print(f"Error: InvalidIdentityTokenException - {e}")
        raise
    except Exception as e:
        print(f"Error: An unexpected error occurred - {e}")
        raise

# Rest of your code remains unchanged
# ...

# Entry point of the script
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Copy AMI from source account to destination account.')
    parser.add_argument('--source', type=str, help='Source AWS account ID')
    parser.add_argument('--source_region', type=str, help='Source AWS region')
    parser.add_argument('--ami', type=str, help='Source AMI ID to copy')
    parser.add_argument('--target', type=str, help='Destination AWS account ID')
    parser.add_argument('--target_region', type=str, help='Destination AWS region')
    args = parser.parse_args()

    # Call the function to get and use AWS SSO credentials
    sso_access_token, sso_session_obj = sso_session()

    # Use the obtained SSO credentials to copy the AMI between accounts
    copy_ami(args.source, args.source_region, args.ami, args.target, args.target_region, sso_access_token, sso_session_obj)

