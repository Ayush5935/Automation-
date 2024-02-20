import argparse
import boto3
from itertools import combinations
import dash
from dash import html, dcc
from dash.dependencies import Input, Output
from dash_cytoscape import Cytoscape
import dash_mantine_components as dmc

def fetch_aws_data(account, region, ipv4, eni, subnet, route_table, destination_ipv4, tgw):
    session = boto3.Session(region_name=region)
    ec2_client = session.client('ec2')
    
    eni_details = [{'label': eni['NetworkInterfaceId'], 'value': eni['NetworkInterfaceId']} for eni in ec2_client.describe_network_interfaces()['NetworkInterfaces']]
    subnet_details = [{'label': subnet['SubnetId'], 'value': subnet['SubnetId']} for subnet in ec2_client.describe_subnets()['Subnets']]
    route_table_details = [{'label': rt['RouteTableId'], 'value': rt['RouteTableId']} for rt in ec2_client.describe_route_tables()['RouteTables']]
    tgw_details = [{'label': tgw['TransitGatewayId'], 'value': tgw['TransitGatewayId']} for tgw in ec2_client.describe_transit_gateways()['TransitGateways']]
    
    tgw_attachments_response = ec2_client.describe_transit_gateway_attachments(Filters=[{'Name': 'transit-gateway-id', 'Values': [tgw]}])
    tgw_attachments = tgw_attachments_response.get('TransitGatewayAttachments', [])
    
    vpc_id = eni_details[0]['VpcId'] if eni_details else None
    vpc_details = [{'label': vpc_id, 'value': vpc_id}] if vpc_id else []
    
    return eni_details, subnet_details, route_table_details, tgw_details, tgw_attachments, vpc_details

def get_cross_region_tgw_connections(region, tgw_attachments):
    cross_region_connections = []
    for attachment in tgw_attachments:
        if attachment['TransitGatewayRegion'] != region:
            cross_region_connections.append({
                'region': attachment['TransitGatewayRegion'],
                'tgw_id': attachment['TransitGatewayId'],
                'attachment_id': attachment['TransitGatewayAttachmentId']
            })
    return cross_region_connections

def aws_network_graph(region, eni_details, subnet_details, route_table_details, tgw_details, tgw_attachments, vpc_details, cross_region_tgw_connections):
    elements = []
    
    vpc_id = vpc_details[0]["label"] if vpc_details else "VPC not available"
    eni_id = eni_details[0]["label"] if eni_details else "ENI not available"
    subnet_id = subnet_details[0]["label"] if subnet_details else "Subnet not available"
    route_table_id = route_table_details[0]["label"] if route_table_details else "Route Table not available"
    tgw_id = tgw_details[0]["label"] if tgw_details else "Transit Gateway not available"
    
    tgw_attachment_id = tgw_attachments[0]["TransitGatewayAttachmentId"] if tgw_attachments else "Transit Gateway Attachment not available"
    
    tgw_route_table_id = tgw_attachments[0]['Association'].get('TransitGatewayRouteTableId') if tgw_attachments else "TGW Route Table ID not available"
    
    elements.append({'data': {'id': 'vpc', 'label': f'VPC {vpc_id}'}})
    elements.append({'data': {'id': 'eni', 'label': f'ENI {eni_id}'}})
    elements.append({'data': {'id': 'subnet', 'label': f'Subnet {subnet_id}'}})
    elements.append({'data': {'id': 'route_table', 'label': f'Route Table {route_table_id}'}})
    elements.append({'data': {'id': 'tgw', 'label': f'Transit Gateway {tgw_id}'}})
    elements.append({'data': {'id': 'tgw_rtb', 'label': f'Tgw Route Table ID {tgw_route_table_id}'}})
    elements.append({'data': {'id': 'tgw_attachment', 'label': f'Transit Gateway Attachment {tgw_attachment_id}'}})
    
    elements.append({'data': {'source': 'vpc', 'target': 'eni'}})
    elements.append({'data': {'source': 'eni', 'target': 'subnet'}})
    elements.append({'data': {'source': 'subnet', 'target': 'route_table'}})
    elements.append({'data': {'source': 'route_table', 'target': 'tgw'}})
    elements.append({'data': {'source': 'tgw', 'target': 'tgw_attachment'}})
    elements.append({'data': {'source': 'tgw_attachment', 'target': 'tgw_rtb'}})
    
    for connection in cross_region_tgw_connections:
        elements.append({'data': {'id': f"cross_tgw_{connection['tgw_id']}", 'label': f'Cross Region TGW {connection["tgw_id"]}'}})
        elements.append({'data': {'source': 'vpc', 'target': f'cross_tgw_{connection["tgw_id"]}'}})
    
    return elements

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate and visualize AWS network graph.')
    parser.add_argument('--account', help='AWS account ID', required=True)
    parser.add_argument('--region', help='AWS region', required=True)
    parser.add_argument('--ipv4', help='Source Private IPv4', required=True)
    parser.add_argument('--eni', help='Source ENI', required=True)
    parser.add_argument('--subnet', help='Source Subnet ID', required=True)
    parser.add_argument('--route-table', help='Source Route Table ID', required=True)
    parser.add_argument('--destination-ipv4', help='Destination Private IPv4', required=True)
    parser.add_argument('--tgw', help='Source TGW', required=True)
    args = parser.parse_args()
    
    eni_details, subnet_details, route_table_details, tgw_details, tgw_attachments, vpc_details = fetch_aws_data(args.account, args.region, args.ipv4, args.eni, args.subnet, args.route_table, args.destination_ipv4, args.tgw)
    cross_region_tgw_connections = get_cross_region_tgw_connections(args.region, tgw_attachments)
    elements = aws_network_graph(args.region, eni_details, subnet_details, route_table_details, tgw_details, tgw_attachments, vpc_details, cross_region_tgw_connections)
    
    app = dash.Dash(__name__)
    
    app.layout = html.Div([
        Cytoscape(
            id='cytoscape-elements-stylesheet',
            layout={'name': 'preset'},
            style={'width': '100%', 'height': '800px'},
            elements=elements
        )
    ])
    
    app.run_server(debug=True)
