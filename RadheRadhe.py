import boto3
import argparse
from botocore.exceptions import WaiterError
from boto3.session import Session
import webbrowser
from time import sleep

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

    print(f"Please authorize the application by visiting: {url}")

    # Open the authorization URL in the default web browser
    webbrowser.open(url, new=2, autoraise=True)

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

def copy_ami(source, source_region, ami, target, target_region, sso_session):
    access_token, primary_session = sso_session()

    if access_token is None:
        print("Failed to obtain access token. Exiting.")
        return

    kms_key_id = 'arn:aws:kms:us-west-2:346687249423:key/3cd4107b-98d1-486a-972c-b4734c735a69'

    # Use primary_session to get the EC2 client for both source and target
    ec2_source = primary_session.client('ec2', region_name=source_region)
    ec2_destination = primary_session.client('ec2', region_name=target_region)

    # Rest of your code...
    # Note: Make sure to properly handle instances and IDs based on your use case.

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Copy AMI from source account to destination account.')
    parser.add_argument('--source', type=str, help='Source AWS account ID')
    parser.add_argument('--source_region', type=str, help='Source AWS region')
    parser.add_argument('--ami', type=str, help='Source AMI ID to copy')
    parser.add_argument('--target', type=str, help='Destination AWS account ID')
    parser.add_argument('--target_region', type=str, help='Destination AWS region')

    args = parser.parse_args()

    copy_ami(args.source, args.source_region, args.ami, args.target, args.target_region, sso_session)
