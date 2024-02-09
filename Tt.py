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

# Function to retrieve ENI details
def get_eni_details(eni_id):
    try:
        response = client.describe_network_interfaces(NetworkInterfaceIds=[eni_id])
        eni_details = response.get('NetworkInterfaces', [])
        return eni_details[0] if eni_details else None
    except Exception as e:
        print(f"Error retrieving ENI details for {eni_id}: {e}")
        return None

# Function to export data to CSV
def export_to_csv(data, filename):
    if not data:
        print(f"No data to export for {filename}")
        return
    try:
        with open(filename, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['eni_id', 'privateIPAddress', 'Type'])  # Write header row
            for item in data:
                writer.writerow(item)
        print(f"Data exported to {filename} successfully.")
    except Exception as e:
        print(f"Error exporting data to {filename}: {e}")

# Main function
def main():
    # Get mirror sessions details
    mirror_sessions = get_mirror_sessions()
    
    # Extract ENI details from mirror sessions and collect private IPv4 addresses
    eni_ipv4_data = []
    for session in mirror_sessions:
        eni_id = session.get('NetworkInterfaceId')
        if eni_id:
            eni_details = get_eni_details(eni_id)
            if eni_details:
                private_ipv4s = eni_details.get('PrivateIpAddresses', [])
                for private_ipv4 in private_ipv4s:
                    eni_ipv4_data.append([
                        eni_id,
                        private_ipv4.get('PrivateIpAddress', 'N/A'),
                        'Primary' if private_ipv4.get('Primary', False) else 'Secondary'
                    ])
    
    # Export ENI IPv4 data to CSV
    export_to_csv(eni_ipv4_data, 'eni_ipv4_addresses.csv')

if __name__ == "__main__":
    main()
