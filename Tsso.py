import boto3
import argparse
from botocore.exceptions import WaiterError
from time import sleep
import webbrowser

region = 'us-west-2'


def sso_session():
    session = boto3.Session()
    start_url = 'https://d-92670ca28f.awsapps.com/start#/'
    sso_oidc = session.client('sso-oidc', region_name=region)
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
    sso = session.client('sso', region_name=region)

    return access_token, sso


def copy_ami(source, source_region, ami, target, target_region, sso_access_token, sso_session):
    source_ec2 = sso_session.client('ec2', region_name=source_region)

    # Copy the AMI to the source account
    response_source = source_ec2.copy_image(
        SourceImageId=ami,
        SourceRegion=source_region,
        Name='CopiedAMI_Source',
        Encrypted=True,
        KmsKeyId='arn:aws:kms:us-west-2:346687249423:key/3cd4107b-98d1-486a-972c-b4734c735a69'
    )
    copied_ami_id_source = response_source['ImageId']
    print(f"Copying AMI {ami} to source account {source}... Please wait...")

    try:
        source_ec2.get_waiter('image_available').wait(ImageIds=[copied_ami_id_source])
    except WaiterError as e:
        print(f"Error waiting for copied AMI in source account: {e}")

    source_ec2.modify_image_attribute(
        ImageId=copied_ami_id_source,
        Attribute='launchPermission',
        LaunchPermission={'Add': [{'UserId': target}]}
    )
    print(f"Sharing AMI {copied_ami_id_source} with destination account {target}... Please wait...")

    target_ec2 = sso_session.client('ec2', region_name=target_region)
    copied_ami_source = source_ec2.describe_images(ImageIds=[copied_ami_id_source])['Images'][0]

    instance_id, new_ami_id = assume_role_and_create_instance(target, target_region, copied_ami_id_source,
                                                              instance_name="CopiedInstance", sso_session=sso_session)
    print(f"Instance ID: {instance_id}")
    print(f"New AMI ID created from the instance {instance_id}: {new_ami_id}")

    delete_confirmation = input("Do you want to delete the copied resources? (Y/N): ").strip().lower()
    if delete_confirmation == 'y':
        target_ec2 = assume_role(target, target_region)
        delete_resources(source_ec2, copied_ami_source['ImageId'],
                         copied_ami_source['BlockDeviceMappings'][0]['Ebs']['SnapshotId'], target_ec2, new_ami_id,
                         instance_id)


def assume_role_and_create_instance(target, target_region, copied_ami_id, instance_name="CopiedInstance", sso_session=None):
    assumed_role_credentials = assume_role(target, target_region, sso_session)
    target_ec2 = boto3.client(
        'ec2',
        region_name=target_region,
        aws_access_key_id=assumed_role_credentials['AccessKeyId'],
        aws_secret_access_key=assumed_role_credentials['SecretAccessKey'],
        aws_session_token=assumed_role_credentials['SessionToken']
    )
    response_run_instance = target_ec2.run_instances(
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
    target_ec2.get_waiter('instance_running').wait(InstanceIds=[instance_id])
    print(f"EC2 instance {instance_id} is now running.")
    response_create_ami = target_ec2.create_image(
        InstanceId=instance_id,
        Name=f'NewAMI_{instance_name}',
        Description=f'AMI created from instance {instance_id}',
        NoReboot=True
    )
    new_ami_id = response_create_ami['ImageId']
    target_ec2.get_waiter('image_available').wait(ImageIds=[new_ami_id])
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
    snapshot_id_destination = ec2_destination.describe_images(ImageIds=[ami_id_destination])['Images'][0][
        'BlockDeviceMappings'][0]['Ebs']['SnapshotId']
    ec2_destination.delete_snapshot(SnapshotId=snapshot_id_destination)
    print(f"Deleted Snapshot {snapshot_id_destination} of AMI {ami_id_destination} from Target Account")


def assume_role(target, region, sso_session=None):
    sts_client = sso_session.client('sts') if sso_session else boto3.client('sts')
    role_arn = f"arn:aws:iam::{target}:role/ami_copy_role"
    assumed_role = sts_client.assume_role(
        RoleArn=role_arn,
        RoleSessionName="AssumedRoleSession"
    )
    return assumed_role['Credentials']


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Copy AMI from source account to destination account.')
    parser.add_argument('--source', type=str, help='Source AWS account ID')
    parser.add_argument('--source_region', type=str, help='Source AWS region')
    parser.add_argument('--ami', type=str, help='Source AMI ID to copy')
    parser.add_argument('--target', type=str, help='Destination AWS account ID')
    parser.add_argument('--target_region', type=str, help='Destination AWS region')
    args = parser.parse_args()
    sso_access_token, sso_session_obj = sso_session()
    copy_ami(args.source, args.source_region, args.ami, args.target, args.target_region, sso_access_token, sso_session_obj)






def copy_ami(source, source_region, ami, target, target_region, sso_access_token, sso_session):
    # Obtain the role credentials using SSO
    role_creds = sso_session.get_role_credentials(
        roleName='DishWPaaSAdministrator',
        accountId=source,
        accessToken=sso_access_token,
    )['roleCredentials']

    # Create a new session with the obtained credentials
    session_with_role = boto3.Session(
        aws_access_key_id=role_creds['accessKeyId'],
        aws_secret_access_key=role_creds['secretAccessKey'],
        aws_session_token=role_creds['sessionToken'],
    )

    # Create an EC2 client using the new session
    source_ec2 = session_with_role.client('ec2', region_name=source_region)

    # Rest of the code remains the same
    # ...
