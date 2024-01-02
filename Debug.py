def delete_resources(ec2_source, ami_id_source, snapshot_id_source, target_role_name, target_region, ami_id_destination, instance_id, sso_session):
    try:
        # Delete resources in the source account
        ec2_source.deregister_image(ImageId=ami_id_source)
        print(f"Deleted AMI from Source Account {ami_id_source}")

        ec2_source.delete_snapshot(SnapshotId=snapshot_id_source)
        print(f"Deleted Snapshot {snapshot_id_source} of AMI {ami_id_source} from Source Account")

        # Assume the role in the target account
        target_role_creds = sso_session.get_role_credentials(
            roleName=target_role_name,
            accountId=args.target,
            accessToken=sso_access_token,
        )['roleCredentials']

        target_session = boto3.Session(
            aws_access_key_id=target_role_creds['accessKeyId'],
            aws_secret_access_key=target_role_creds['secretAccessKey'],
            aws_session_token=target_role_creds['sessionToken'],
            region_name=target_region
        )
        target_ec2 = target_session.client('ec2')

        # Delete resources in the target account
        target_ec2.deregister_image(ImageId=ami_id_destination)
        print(f"Deleted AMI from Target Account {ami_id_destination}")

        snapshot_id_destination = target_ec2.describe_images(ImageIds=[ami_id_destination])['Images'][0]['BlockDeviceMappings'][0]['Ebs']['SnapshotId']
        target_ec2.delete_snapshot(SnapshotId=snapshot_id_destination)
        print(f"Deleted Snapshot {snapshot_id_destination} of AMI {ami_id_destination} from Target Account")

        # Terminate the EC2 instance in the target account
        target_ec2.terminate_instances(InstanceIds=[instance_id])
        print(f"Terminated EC2 instance from Target Account {instance_id}")

    except Exception as e:
        print(f"Error deleting resources: {e}")
        raise

# Call the updated function
delete_resources(source_ec2, copied_ami_source['ImageId'], copied_ami_source['BlockDeviceMappings'][0]['Ebs']['SnapshotId'], 'DishWPaaSAdministrator', args.target_region, new_ami_id, instance_id, sso_session_obj)
