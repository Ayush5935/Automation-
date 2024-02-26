# Import the required modules
import csv
import boto3
import subprocess
import json
import datetime

# Define the input and output file names and locations
input_file = "input.csv"
output_file = "output.csv"

# Define the AWS SSO login URL
sso_url = "https://d-92670ca28f.awsapps.com/start#/"  # Update with your start URL

# Define a function to obtain the SSO access token using the device authorization grant flow
def get_sso_access_token():
    session = boto3.session.Session()
    region = 'us-west-2'  # Update with your preferred region
    sso_oidc = session.client('sso-oidc', region_name=region)
    client_creds = sso_oidc.register_client(clientName='myapp', clientType='public')
    device_authorization = sso_oidc.start_device_authorization(
        clientId=client_creds['clientId'],
        clientSecret=client_creds['clientSecret'],
        startUrl=sso_url
    )
    print(f"Open the following URL in your browser to authenticate: {device_authorization['verificationUriComplete']}")
    print(f"Waiting for authentication...")
    expires_in = device_authorization['expiresIn']
    interval = device_authorization['interval']

    for _ in range(1, expires_in // interval + 1):
        try:
            token = sso_oidc.create_token(
                grantType='urn:ietf:params:oauth:grant-type:device_code',
                deviceCode=device_authorization['deviceCode'],
                clientId=client_creds['clientId'],
                clientSecret=client_creds['clientSecret']
            )
            return token['accessToken'], token['expiresAt']
        except sso_oidc.exceptions.AuthorizationPendingException:
            pass
        except Exception as e:
            print(f"Error: {e}")
            return None, None

# Define a function to refresh the SSO access token if it is expired or close to expiration
def refresh_sso_access_token(access_token, expires_at):
    # Define a buffer time of 5 minutes before the expiration time
    buffer_time = 5 * 60
    # Get the current time in UTC
    current_time = datetime.datetime.utcnow()
    # Convert the expiration time from ISO 8601 format to a datetime object
    expires_at = datetime.datetime.fromisoformat(expires_at.replace('Z', '+00:00'))
    # Check if the current time is within the buffer time of the expiration time
    if current_time >= expires_at - datetime.timedelta(seconds=buffer_time):
        # Obtain a new access token using the same SSO URL
        print(f"Refreshing SSO access token...")
        access_token, expires_at = get_sso_access_token()
        if access_token is None:
            print("Failed to obtain SSO access token.")
            return None, None
    # Return the access token and the expiration time
    return access_token, expires_at

# Define a function to obtain the VPC ID and Subnet ID for a given instance ID, region, and access token
def get_vpc_subnet_id(instance_id, region, access_token):
    session = boto3.session.Session()
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
        # Check if the instance has a VPC ID and a Subnet ID
        if 'VpcId' in response['Reservations'][0]['Instances'][0] and 'SubnetId' in response['Reservations'][0]['Instances'][0]:
            vpc_id = response['Reservations'][0]['Instances'][0]['VpcId']
            subnet_id = response['Reservations'][0]['Instances'][0]['SubnetId']
        else:
            # Use a default value of 'None' for the VPC ID and Subnet ID if the instance does not have them
            vpc_id = 'None'
            subnet_id = 'None'
        return vpc_id, subnet_id
    except Exception as e:
        print(f"Error: {e}")
        return None, None

# Define the main logic of the script
def main():
    # Open the input CSV file and read the rows into a list of dictionaries
    with open(input_file, 'r') as f:
        reader = csv.DictReader(f)
        input_data = list(reader)
    
    # Initialize an empty list to store the output data
    output_data = []

    # Loop through each row of the input data
    for row in input_data:
        # Obtain the account ID, instance ID, and region
        account_id = row['Account ID']
        instance_id = row['Instance ID']
        region = row['Region']

        # Call the refresh_sso_access_token function to get a valid SSO access token for the current account and region
        access_token, expires_at = refresh_sso_access_token(None, None)
        if access_token is None:
            print(f"Failed to get SSO access token for account {account_id} and region {region}.")
            continue
        
        # Call the get_vpc_subnet_id function to get the VPC ID and Subnet ID for the current instance ID and region
        vpc_id, subnet_id = get_vpc_subnet_id(instance_id, region, access_token)
        if vpc_id is None or subnet_id is None:
            print(f"Failed to get VPC ID and Subnet ID for instance {instance_id} in region {region}.")
            continue
        
        # Append the results to the output data list as a dictionary
        output_data.append({
            'Account ID': account_id,
            'Instance ID': instance_id,
            'VPC ID': vpc_id,
            'Subnet ID': subnet_id
        })
    
    # Open the output CSV file and write the output data list into it
    with open(output_file, 'w') as f:
        writer = csv.DictWriter(f, fieldnames=['Account ID', 'Instance ID', 'VPC ID', 'Subnet ID'])
        writer.writeheader()
        writer.writerows(output_data)
    
    # Print a success message
    print(f"Successfully wrote {len(output_data)} rows to {output_file}.")

# Execute the main function
if __name__ == '__main__':
    main()
