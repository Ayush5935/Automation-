import boto3
import csv

# Initialize Boto3 client for EC2
client = boto3.client('ec2')

# Function to retrieve network interfaces details along with their associated source and target
def get_network_interfaces():
    try:
        response = client.describe_network_interfaces()
        network_interfaces = response.get('NetworkInterfaces', [])
        formatted_data = []
        for interface in network_interfaces:
            interface_id = interface.get('NetworkInterfaceId', '')
            source, target = get_source_target(interface_id)
            formatted_data.append({
                'NetworkInterfaceId': interface_id,
                'Source': source,
                'Target': target
            })
        return formatted_data
    except Exception as e:
        print(f"Error retrieving network interfaces: {e}")
        return []

# Function to retrieve source and target associated with a network interface
def get_source_target(interface_id):
    try:
        response = client.describe_traffic_mirror_sessions(Filters=[{'Name': 'NetworkInterfaceId', 'Values': [interface_id]}])
        sessions = response.get('TrafficMirrorSessions', [])
        source = []
        target = []
        for session in sessions:
            source_id = session.get('SourceId', '')
            target_id = session.get('TargetId', '')
            if source_id:
                source.append(source_id)
            if target_id:
                target.append(target_id)
        return ','.join(source), ','.join(target)
    except Exception as e:
        print(f"Error retrieving source and target info for {interface_id}: {e}")
        return '', ''

# Function to export data to CSV
def export_to_csv(data, filename):
    if not data:
        print(f"No data to export for {filename}")
        return
    try:
        with open(filename, 'w', newline='') as csvfile:
            fieldnames = ['NetworkInterfaceId', 'Source', 'Target']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for item in data:
                writer.writerow(item)
        print(f"Data exported to {filename} successfully.")
    except Exception as e:
        print(f"Error exporting data to {filename}: {e}")

# Main function
def main():
    # Get network interfaces details with source and target
    network_interfaces = get_network_interfaces()
    export_to_csv(network_interfaces, 'network_interfaces_with_source_target.csv')

if __name__ == "__main__":
    main()
