def create_instance_and_ami(ec2_client, ami_id, instance_name="CopiedInstance"):
    # Launch an EC2 instance using the copied AMI
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

# Add this code at the end of the copy_ami function
instance_id, new_ami_id = create_instance_and_ami(ec2_destination, copied_ami_id_destination)
print(f"Instance ID: {instance_id}")
print(f"New AMI ID created from the instance: {new_ami_id}")
￼Enter
