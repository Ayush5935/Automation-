import boto3
import csv

# Initialize Boto3 client
client = boto3.client('networkmanager')

# Function to retrieve global network ID
def get_global_network_id():
    response = client.describe_global_networks()
    global_networks = response.get('GlobalNetworks', [])
    if global_networks:
        return global_networks[0]['GlobalNetworkId']
    else:
        return None

# Function to retrieve mirror sessions details
def get_mirror_sessions(global_network_id):
    response = client.describe_global_networks()
    if not global_network_id:
        print("No global network found.")
        return []
    response = client.describe_transit_gateway_attachments(GlobalNetworkId=global_network_id)
    attachments = response.get('TransitGatewayAttachments', [])
    if attachments:
        mirror_sessions = attachments[0]['Association']['MirrorConfiguration']['MirrorSessions']
        return mirror_sessions
    else:
        print("No mirror sessions found.")
        return []

# Function to retrieve mirror targets details
def get_mirror_targets(global_network_id):
    response = client.describe_global_networks()
    if not global_network_id:
        print("No global network found.")
        return []
    response = client.describe_transit_gateway_attachments(GlobalNetworkId=global_network_id)
    attachments = response.get('TransitGatewayAttachments', [])
    if attachments:
        mirror_targets = attachments[0]['Association']['MirrorConfiguration']['MirrorTargets']
        return mirror_targets
    else:
        print("No mirror targets found.")
        return []

# Function to retrieve mirror filters details
def get_mirror_filters(global_network_id):
    response = client.describe_global_networks()
    if not global_network_id:
        print("No global network found.")
        return []
    response = client.describe_transit_gateway_attachments(GlobalNetworkId=global_network_id)
    attachments = response.get('TransitGatewayAttachments', [])
    if attachments:
        mirror_filters = attachments[0]['Association']['MirrorConfiguration']['MirrorFilters']
        return mirror_filters
    else:
        print("No mirror filters found.")
        return []

# Function to export data to CSV
def export_to_csv(data, filename):
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(data[0].keys()) if data else None  # Write header row if data is present
        for item in data:
            writer.writerow(item.values())

# Main function
def main():
    global_network_id = get_global_network_id()

    # Get mirror sessions details
    mirror_sessions = get_mirror_sessions(global_network_id)
    export_to_csv(mirror_sessions, 'mirror_sessions.csv')

    # Get mirror targets details
    mirror_targets = get_mirror_targets(global_network_id)
    export_to_csv(mirror_targets, 'mirror_targets.csv')

    # Get mirror filters details
    mirror_filters = get_mirror_filters(global_network_id)
    export_to_csv(mirror_filters, 'mirror_filters.csv')

    print("CSV files exported successfully.")

if __name__ == "__main__":
    main()
