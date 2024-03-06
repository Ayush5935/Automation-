import argparse
import boto3
import dash
from dash import html, dcc
from dash.dependencies import Input, Output
from dash_cytoscape import Cytoscape
import dash_mantine_components as dmc
import dash_bootstrap_components as dbc
import ipaddress

def calculate_ip_distance(ip1, ip2):
    try:
        ip1 = ipaddress.IPv4Address(ip1)
        ip2 = ipaddress.IPv4Address(ip2)
        return abs(int(ip1) - int(ip2))
    except ValueError:
        return float('inf')  # Return infinity if IP addresses are invalid

def fetch_aws_data(account, region, ipv4, eni, subnet, route_table, destination_ipv4, tgw):
    session = boto3.Session(region_name=region)
    ec2_client = session.client('ec2')

    # Fetch ENI details
    eni_details = [{'label': eni['NetworkInterfaceId'], 'value': eni['NetworkInterfaceId']} for eni in ec2_client.describe_network_interfaces(NetworkInterfaceIds=[eni])['NetworkInterfaces']]

    # Fetch Subnet details
    subnet_id = eni_details[0]['subnet_id']
    subnet_details = [{'label': subnet['SubnetId'], 'value': subnet['SubnetId']} for subnet in ec2_client.describe_subnets(SubnetIds=[subnet_id])['Subnets']]

    # Fetch VPC details
    vpc_id = subnet_details[0]['vpc_id']
    vpc_details = [{'label': vpc['VpcId'], 'value': vpc['VpcId']} for vpc in ec2_client.describe_vpcs(VpcIds=[vpc_id])['Vpcs']]

    # Fetch Route Table details
    route_table_id = subnet_details[0]['route_table_id']
    route_table_details = [{'label': rt['RouteTableId'], 'value': rt['RouteTableId']} for rt in ec2_client.describe_route_tables(RouteTableIds=[route_table_id])['RouteTables']]

    # Check routes in the route table
    for rt in route_table_details:
        routes = ec2_client.describe_route_tables(RouteTableIds=[rt['value']])['RouteTables'][0]['Routes']
        for route in routes:
            if 'NatGatewayId' in route or 'GatewayId' in route:  # Check for NAT or IGW
                break
        else:
            continue
        break  # Break the loop if NAT or IGW found

    # Fetch TGW details
    tgw_details = [{'label': tgw['TransitGatewayId'], 'value': tgw['TransitGatewayId']} for tgw in ec2_client.describe_transit_gateways(TransitGatewayIds=[tgw])['TransitGateways']]

    # Fetch TGW Route Table details
    tgw_attachments = ec2_client.describe_transit_gateway_attachments(Filters=[{'Name': 'transit-gateway-id', 'Values': [tgw]}])['TransitGatewayAttachments']
    tgw_route_table_details = []
    for attachment in tgw_attachments:
        tgw_route_table_id = attachment['Association']['TransitGatewayRouteTableId']
        tgw_route_table_details.append({'label': tgw_route_table_id, 'value': tgw_route_table_id})

    # Check if any retrieved resource is too close to the destination IP address
    close_resources = []
    for resource in [eni_details, subnet_details, route_table_details, vpc_details, tgw_details, tgw_route_table_details]:
        for item in resource:
            if calculate_ip_distance(destination_ipv4, item['label']) < 10:  # Set the threshold as needed
                close_resources.append(item['label'])

    return eni_details, subnet_details, route_table_details, vpc_details, tgw_details, tgw_route_table_details, tgw_attachments, close_resources

# The rest of the code remains the same...

