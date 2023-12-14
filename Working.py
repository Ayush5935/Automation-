import boto3

target_account_id = '123XXXXXXX'
source_profile = 'aws-cli-profile'
role_on_target_account = 'arn:aws:iam::TARGET_ACCOUNT_ID:role/ROLE_NAME'  # Replace with actual target account ID and role name
source_region = 'us-east-1'
target_region = 'us-east-1'

# Specify the specific AMI IDs you want to copy
ami_ids_to_copy = ['ami-12345678', 'ami-87654321']

def get_main_session():
    session = boto3.Session(profile_name=source_profile, region_name=source_region)
    return session

def get_temp_cred(session, role_arn, account_id):
    sts_client = session.client('sts')
    response = sts_client.assume_role(
        RoleArn=role_arn,
        RoleSessionName=account_id
    )
    return response['Credentials']

def get_temp_session(cred, region):
    temp_session = boto3.Session(
        aws_access_key_id=cred['AccessKeyId'],
        aws_secret_access_key=cred['SecretAccessKey'],
        aws_session_token=cred['SessionToken'],
        region_name=region
    )
    return temp_session

def copy_ami(session, source_region, target_region, ami_id):
    for i in ami_id:
        client = session.client('ec2', region_name=target_region)
        response = client.copy_image(
            Description='Encrypted Golden Image',
            Encrypted=True,
            KmsKeyId='arn:aws:kms:us-east-1:TARGET_ACCOUNT_ID:key/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx',  # Replace with actual KMS Key ID
            Name='Demo-Copy-AMI',
            SourceImageId=i,
            SourceRegion=source_region
        )
        print(f"AMI {i} copied. New AMI ID: {response['ImageId']}")

def main():
    session = get_main_session()
    temp_cred = get_temp_cred(session, role_on_target_account, target_account_id)
    temp_session = get_temp_session(temp_cred, target_region)
    copy_ami(temp_session, source_region, target_region, ami_ids_to_copy)

if __name__ == '__main__':
    main()
