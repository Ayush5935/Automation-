# ...

# Get information about the copied AMI in the target account
response = target_ec2.describe_images(ImageIds=[ami_id_destination])

if 'Images' in response and response['Images']:
    snapshot_id_destination = response['Images'][0]['BlockDeviceMappings'][0]['Ebs']['SnapshotId']
    print(f"Snapshot ID associated with AMI {ami_id_destination} in the target account: {snapshot_id_destination}")

    # Delete the snapshot associated with the AMI in the target account
    try:
        target_ec2.delete_snapshot(SnapshotId=snapshot_id_destination)
        print(f"Deleted Snapshot {snapshot_id_destination} of AMI {ami_id_destination} from Target Account")
    except Exception as snapshot_error:
        print(f"Error deleting snapshot {snapshot_id_destination} associated with AMI {ami_id_destination}: {snapshot_error}")
else:
    print(f"No information found for AMI {ami_id_destination} in the target account.")

# ...
