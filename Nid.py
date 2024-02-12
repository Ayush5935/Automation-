import boto3
import csv

client = boto3.client('ec2')

def get_mirror_sessions():
    try:
        response = client.describe_traffic_mirror_sessions()
        mirror_sessions = response.get('TrafficMirrorSessions', [])
        return mirror_sessions
    except Exception as e:
        print(f"Error retrieving mirror sessions: {e}")
        return []

def get_eni_details(eni_id):
    try:
        response = client.describe_network_interfaces(NetworkInterfaceIds=[eni_id])
        eni_details = response.get('NetworkInterfaces', [])
        return eni_details[0] if eni_details else None
    except Exception as e:
        print(f"Error retrieving ENI details for {eni_id}: {e}")
        return None

def export_to_csv(data, filename):
    if not data:
        print(f"No data to export for {filename}")
        return
    try:
        with open(filename, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['eni_id', 'privateIPAddress', 'Primary', 'OwnerId'])  # Updated header row
            for item in data:
                writer.writerow(item)
        print(f"Data exported to {filename} successfully.")
    except Exception as e:
        print(f"Error exporting data to {filename}: {e}")

def main():
    mirror_sessions = get_mirror_sessions()
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
                        'True' if private_ipv4.get('Primary', False) else 'False',
                        eni_details.get('OwnerId', 'N/A')  # Added OwnerId field
                    ])
    export_to_csv(eni_ipv4_data, 'NetworkInterfaceId.csv')

if __name__ == "__main__":
    main()
￼Enter
