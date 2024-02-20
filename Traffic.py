import boto3
import csv

client = boto3.client('ec2')

def paginate(method, **kwargs):
    """
    Paginate the AWS API calls to retrieve all available data
    """
    paginator = client.get_paginator(method)
    for page in paginator.paginate(**kwargs):
        for item in page.get('TrafficMirrorSessions', []):
            yield item

def get_mirror_sessions():
    """
    Retrieve mirror sessions details using pagination
    """
    try:
        return list(paginate('describe_traffic_mirror_sessions'))
    except Exception as e:
        print(f"Error retrieving mirror sessions: {e}")
        return []

def get_mirror_targets():
    """
    Retrieve mirror targets details using pagination
    """
    try:
        return list(paginate('describe_traffic_mirror_targets'))
    except Exception as e:
        print(f"Error retrieving mirror targets: {e}")
        return []

def export_to_csv(data, filename):
    """
    Export data to CSV file
    """
    if not data:
        print(f"No data to export for {filename}")
        return
    try:
        with open(filename, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(data[0].keys()) if data else None
            for item in data:
                writer.writerow(item.values())
        print(f"Data exported to {filename} successfully.")
    except Exception as e:
        print(f"Error exporting data to {filename}: {e}")

def main():
    mirror_sessions = get_mirror_sessions()
    export_to_csv(mirror_sessions, 'mirror_sessions.csv')

    mirror_targets = get_mirror_targets()
    export_to_csv(mirror_targets, 'mirror_targets.csv')

if __name__ == "__main__":
    main()
