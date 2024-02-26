import csv
import boto3
import datetime
import webbrowser

# Define the input and output file names and locations
input_file = "input.csv"
output_file = "output.csv"

# Define the AWS SSO login URL
sso_url = "https://d-92670ca28f.awsapps.com/start#/"  # Update with your start URL

# Define a function to obtain the SSO access token using the device authorization grant flow
def get_sso_access_token():
    session = boto3.Session()
    region = 'us-west-2'  # Update with your preferred region
    sso_oidc = session.client('sso-oidc', region_name=region)
    client_creds = sso_oidc.register_client(clientName='myapp', clientType='public')
    device_authorization = sso_oidc.start_device_authorization(
        clientId=client_creds['clientId'],
        clientSecret=client_creds['clientSecret'],
        startUrl=sso_url
    )
    url = device_authorization['verificationUriComplete']
    device_code = device_authorization['deviceCode']
    expires_in = device_authorization['expiresIn']
    interval = device_authorization['interval']
    webbrowser.open(url, autoraise=True)
    print(f"Open the following URL in your browser to authenticate: {url}")
    print(f"Waiting for authentication...")
    for _ in range(1, expires_in // interval + 1):
        try:
            token = sso_oidc.create_token(
                grantType='urn:ietf:params:oauth:grant-type:device_code',
                deviceCode=device_code,
                clientId=client_creds['clientId'],
                clientSecret=client_creds['clientSecret']
            )
            expires_at = datetime.datetime.utcnow() + datetime.timedelta(seconds=token['expiresIn'])
            return token['accessToken'], expires_at
        except sso_oidc.exceptions.AuthorizationPendingException:
            pass
        except Exception as e:
            print(f"Error: {e}")
            return None, None

# Define a function to refresh the SSO access token if it is expired or close to expiration
def refresh_sso_access_token(access_token, expires_at):
    buffer_time = 5 * 60  # 5 minutes
    current_time = datetime.datetime.utcnow()
    if expires_at is None or current_time >= expires_at - datetime.timedelta(seconds=buffer_time):
        print(f"Refreshing SSO access token...")
        access_token, expires_at = get_sso_access_token()
        if access_token is None:
            print("Failed to obtain SSO access token.")
            return None, None
    return access_token, expires_at

# Define a function to obtain the VPC ID and Subnet ID for a given instance ID, region, and access token
def get_vpc_subnet_id(instance_id, region, access_token):
    access_token, expires_at = refresh_sso_access_token(access_token, None)
    if access_token is None:
        return None, None

    session = boto3.Session()
    sso = session.client('sso', region_name=region)

    account_id = boto3.client('sts').get_caller_identity().get('Account')
    role_credentials = sso.get_role_credentials(
        roleName='DishWPaaSAdministrator',
        accountId=account_id,
        accessToken=access_token
    )['roleCredentials']

    ec2 = session.client(
        'ec2',
        region_name=region,
        aws_access_key_id=role_credentials['accessKeyId'],
        aws_secret_access_key=role_credentials['secretAccessKey'],
        aws_session_token=role_credentials['sessionToken']
    )

    try:
        response = ec2.describe_instances(InstanceIds=[instance_id])
        if 'VpcId' in response['Reservations'][0]['Instances'][0] and 'SubnetId' in response['Reservations'][0]['Instances'][0]:
            vpc_id = response['Reservations'][0]['Instances'][0]['VpcId']
            subnet_id = response['Reservations'][0]['Instances'][0]['SubnetId']
        else:
            vpc_id = 'None'
            subnet_id = 'None'
        return vpc_id, subnet_id
    except Exception as e:
        print(f"Error: {e}")
        return None, None

# Define the main logic of the script
def main():
    with open(input_file, 'r') as f:
        reader = csv.DictReader(f)
        input_data = list(reader)
    
    output_data = []

    for row in input_data:
        account_id = row['Account ID']
        instance_id = row['Instance ID']
        region = row['Region']

        vpc_id, subnet_id = get_vpc_subnet_id(instance_id, region, None)
        if vpc_id is None or subnet_id is None:
            print(f"Failed to get VPC ID and Subnet ID for instance {instance_id} in region {region}.")
            continue
        
        output_data.append({
            'Account ID': account_id,
            'Instance ID': instance_id,
            'VPC ID': vpc_id,
            'Subnet ID': subnet_id
        })
    
    with open(output_file, 'w') as f:
        writer = csv.DictWriter(f, fieldnames=['Account ID', 'Instance ID', 'VPC ID', 'Subnet ID'])
        writer.writeheader()
        writer.writerows(output_data)
    
    print(f"Successfully wrote {len(output_data)} rows to {output_file}.")

if __name__ == '__main__':
    main()
