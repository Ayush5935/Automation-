import boto3
import csv

# Initialize Boto3 client
client = boto3.client('networkmanager')

# Function to retrieve global network ID
def get_global_network_id():
    response = client.describe_global_networks()
    if 'GlobalNetworks' in response and response['GlobalNetworks']:
        return response['GlobalNetworks'][0]['GlobalNetworkId']
    else:
        raise Exception("No global network found in the AWS account.")

# Function to retrieve mirror sessions details
def get_mirror_sessions(global_network_id):
    response = client.get_transit_gateway_registrations(GlobalNetworkId=global_network_id)
    transit_gateway_arn = response['TransitGatewayRegistrations'][0]['TransitGatewayArn']
    response = client.describe_transit_gateway_attachments(Filters=[{'Name': 'transit-gateway-arn', 'Values': [transit_gateway_arn]}])
    attachment_id = response['TransitGatewayAttachments'][0]['TransitGatewayAttachmentId']
    response = client.describe_transit_gateway_attachments(TransitGatewayAttachmentIds=[attachment_id])
    mirror_sessions = response['TransitGatewayAttachments'][0]['Association']['MirrorConfiguration']['MirrorSessions']
    return mirror_sessions

# Function to retrieve mirror targets details
def get_mirror_targets(global_network_id):
    response = client.get_transit_gateway_registrations(GlobalNetworkId=global_network_id)
    transit_gateway_arn = response['TransitGatewayRegistrations'][0]['TransitGatewayArn']
    response = client.describe_transit_gateway_attachments(Filters=[{'Name': 'transit-gateway-arn', 'Values': [transit_gateway_arn]}])
    attachment_id = response['TransitGatewayAttachments'][0]['TransitGatewayAttachmentId']
    response = client.describe_transit_gateway_attachments(TransitGatewayAttachmentIds=[attachment_id])
    mirror_targets = response['TransitGatewayAttachments'][0]['Association']['MirrorConfiguration']['MirrorTargets']
    return mirror_targets

# Function to retrieve mirror filters details
def get_mirror_filters(global_network_id):
    response = client.get_transit_gateway_registrations(GlobalNetworkId=global_network_id)
    transit_gateway_arn = response['TransitGatewayRegistrations'][0]['TransitGatewayArn']
    response = client.describe_transit_gateway_attachments(Filters=[{'Name': 'transit-gateway-arn', 'Values': [transit_gateway_arn]}])
    attachment_id = response['TransitGatewayAttachments'][0]['TransitGatewayAttachmentId']
    response = client.describe_transit_gateway_attachments(TransitGatewayAttachmentIds=[attachment_id])
    mirror_filters = response['TransitGatewayAttachments'][0]['Association']['MirrorConfiguration']['MirrorFilters']
    return mirror_filters

# Function to export data to CSV
def export_to_csv(data, filename):
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(data[0].keys())  # Write header row
        for item in data:
            writer.writerow(item.values())

try:
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
except Exception as e:
    print("Error:", e)
