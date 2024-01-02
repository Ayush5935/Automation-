def delete_resources(ec2_source, ami_id_source, snapshot_id_source, target, ami_id_destination, instance_id):
    try:
        # Delete resources in the source account
        ec2_source.deregister_image(ImageId=ami_id_source)
        print(f"Deleted AMI from Source Account {ami_id_source}")

        ec2_source.delete_snapshot(SnapshotId=snapshot_id_source)
        print(f"Deleted Snapshot {snapshot_id_source} of AMI {ami_id_source} from Source Account")

        # Delete resources in the target account using assumed role
        role_creds_target = sso_session.get_role_credentials(
            roleName='DishWPaaSAdministrator',
            accountId=target,
            accessToken=sso_access_token,
        )['roleCredentials']

        session_with_role_target = boto3.Session(
            aws_access_key_id=role_creds_target['accessKeyId'],
            aws_secret_access_key=role_creds_target['secretAccessKey'],
            aws_session_token=role_creds_target['sessionToken'],
        )

        target_ec2 = session_with_role_target.client('ec2', region_name=target_region)

        target_ec2.deregister_image(ImageId=ami_id_destination)
        print(f"Deleted AMI from Target Account {ami_id_destination}")

        snapshot_id_destination = target_ec2.describe_images(ImageIds=[ami_id_destination])['Images'][0]['BlockDeviceMappings'][0]['Ebs']['SnapshotId']
        target_ec2.delete_snapshot(SnapshotId=snapshot_id_destination)
        print(f"Deleted Snapshot {snapshot_id_destination} of AMI {ami_id_destination} from Target Account")

        target_ec2.terminate_instances(InstanceIds=[instance_id])
        print(f"Terminated EC2 instance from Target Account {instance_id}")

    except Exception as e:
        print(f"Error deleting resources: {e}")
        raise
￼Enter
