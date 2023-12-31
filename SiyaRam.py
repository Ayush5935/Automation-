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
