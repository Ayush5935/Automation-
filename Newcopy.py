import boto3

def copy_ami(source_access_key, source_secret_key, source_region, source_ami_id, dest_access_key, dest_secret_key, dest_region, dest_kms_key_id):
    # Create EC2 clients with source and destination credentials
    ec2_source = boto3.client('ec2', region_name=source_region,
                              aws_access_key_id=source_access_key,
                              aws_secret_access_key=source_secret_key)

    ec2_dest = boto3.client('ec2', region_name=dest_region,
                             aws_access_key_id=dest_access_key,
                             aws_secret_access_key=dest_secret_key)

    # Copy the source AMI to destination region
    copy_response = ec2_dest.copy_image(
        Name=f"Copied AMI from {source_region} - {source_ami_id}",
        SourceImageId=source_ami_id,
        SourceRegion=source_region,
        Encrypted=True,
        KmsKeyId=dest_kms_key_id
    )

    # Extract the new AMI ID in the destination region
    dest_ami_id = copy_response['ImageId']
    print(f"AMI copied to {dest_region}. New AMI ID: {dest_ami_id}")

if __name__ == '__main__':
    source_access_key = 'your_source_access_key'       # Replace with source AWS access key
    source_secret_key = 'your_source_secret_key'       # Replace with source AWS secret key
    source_region = 'us-west-1'                        # Replace with source region
    source_ami_id = 'ami-xxxxxxxxxxxxxxxxx'            # Replace with source AMI ID

    dest_access_key = 'your_dest_access_key'           # Replace with destination AWS access key
    dest_secret_key = 'your_dest_secret_key'           # Replace with destination AWS secret key
    dest_region = 'us-east-1'                          # Replace with destination region
    dest_kms_key_id = 'arn:aws:kms:us-east-1:222222222222:key/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx'  # Replace with destination KMS Key ID

    copy_ami(source_access_key, source_secret_key, source_region, source_ami_id, dest_access_key, dest_secret_key, dest_region, dest_kms_key_id)
￼Enter
