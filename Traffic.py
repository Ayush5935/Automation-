import boto3
import csv

# Initialize Boto3 client for EC2
client = boto3.client('ec2')

# Function to retrieve mirror sessions details
def get_mirror_sessions():
    try:
        response = client.describe_traffic_mirror_sessions()
        mirror_sessions = response.get('TrafficMirrorSessions', [])
        return mirror_sessions
    except Exception as e:
        print(f"Error retrieving mirror sessions: {e}")
        return []

# Function to retrieve mirror targets details
def get_mirror_targets():
    try:
        response = client.describe_traffic_mirror_targets()
        mirror_targets = response.get('TrafficMirrorTargets', [])
        return mirror_targets
    except Exception as e:
        print(f"Error retrieving mirror targets: {e}")
        return []

# Function to retrieve mirror filters details
def get_mirror_filters():
    try:
        response = client.describe_traffic_mirror_filters()
        mirror_filters = response.get('TrafficMirrorFilters', [])
        return mirror_filters
    except Exception as e:
        print(f"Error retrieving mirror filters: {e}")
        return []

# Function to export data to CSV
def export_to_csv(data, filename):
    if not data:
        print(f"No data to export for {filename}")
        return
    try:
        with open(filename, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(data[0].keys()) if data else None  # Write header row if data is present
            for item in data:
                writer.writerow(item.values())
        print(f"Data exported to {filename} successfully.")
    except Exception as e:
        print(f"Error exporting data to {filename}: {e}")

# Main function
def main():
    # Get mirror sessions details
    mirror_sessions = get_mirror_sessions()
    export_to_csv(mirror_sessions, 'mirror_sessions.csv')

    # Get mirror targets details
    mirror_targets = get_mirror_targets()
    export_to_csv(mirror_targets, 'mirror_targets.csv')

    # Get mirror filters details
    mirror_filters = get_mirror_filters()
    export_to_csv(mirror_filters, 'mirror_filters.csv')

if __name__ == "__main__":
    main()
