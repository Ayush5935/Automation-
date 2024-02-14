import boto3
import csv

def get_all_regions():
    """
    Function to retrieve all AWS regions
    """
    ec2_client = boto3.client('ec2', region_name='us-east-1')
    response = ec2_client.describe_regions()
    return [region['RegionName'] for region in response['Regions']]

def get_mirror_sessions(client):
    """
    Function to retrieve mirror sessions details for a specific region
    """
    try:
        response = client.describe_traffic_mirror_sessions()
        mirror_sessions = response.get('TrafficMirrorSessions', [])
        return mirror_sessions
    except Exception as e:
        print(f"Error retrieving mirror sessions: {e}")
        return []

def get_mirror_targets(client):
    """
    Function to retrieve mirror targets details for a specific region
    """
    try:
        response = client.describe_traffic_mirror_targets()
        mirror_targets = response.get('TrafficMirrorTargets', [])
        return mirror_targets
    except Exception as e:
        print(f"Error retrieving mirror targets: {e}")
        return []

def export_to_csv(data, filename):
    if not data:
        print(f"No data to export for {filename}")
        return
    try:
        with open(filename, 'w', newline='') as csvfile:
            fieldnames = [key for key in data[0].keys() if key != 'Tags']  # Exclude 'Tags' field
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for row in data:
                writer.writerow({key: row[key] for key in fieldnames})
        print(f"Data exported to {filename} successfully.")
    except Exception as e:
        print(f"Error exporting data to {filename}: {e}")

def main():
    regions = get_all_regions()
    for region in regions:
        session = boto3.Session(region_name=region)
        client = session.client('ec2')
        
        mirror_sessions = get_mirror_sessions(client)
        export_to_csv(mirror_sessions, f'mirror_sessions_{region}.csv')
        
        mirror_targets = get_mirror_targets(client)
        export_to_csv(mirror_targets, f'mirror_targets_{region}.csv')

if __name__ == "__main__":
    main()
￼Enter
