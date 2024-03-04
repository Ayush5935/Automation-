import argparse
import boto3
import dash
from dash import html, dcc
from dash.dependencies import Input, Output
from dash_cytoscape import Cytoscape
import dash_mantine_components as dmc
import dash_bootstrap_components as dbc

def fetch_aws_data(account, region, ipv4, eni, subnet, route_table, destination_ipv4, tgw):
    session = boto3.Session(region_name=region)
    ec2_client = session.client('ec2')
    
    # Fetch VPCs
    vpcs = ec2_client.describe_vpcs()['Vpcs']
    vpc_details = [{'label': vpc['VpcId'], 'value': vpc['VpcId']} for vpc in vpcs]

    # Fetch ENIs
    eni_details = [{'label': eni['NetworkInterfaceId'], 'value': eni['NetworkInterfaceId']} for eni in ec2_client.describe_network_interfaces()['NetworkInterfaces']]

    # Fetch Subnets
    subnet_details = [{'label': subnet['SubnetId'], 'value': subnet['SubnetId']} for subnet in ec2_client.describe_subnets()['Subnets']]

    # Fetch Route Tables
    route_table_details = [{'label': rt['RouteTableId'], 'value': rt['RouteTableId']} for rt in ec2_client.describe_route_tables()['RouteTables']]

    # Fetch TGWs
    tgw_details = [{'label': tgw['TransitGatewayId'], 'value': tgw['TransitGatewayId']} for tgw in ec2_client.describe_transit_gateways()['TransitGateways']]

    # Fetch TGW Attachments
    tgw_attachments = ec2_client.describe_transit_gateway_attachments(Filters=[{'Name': 'transit-gateway-id', 'Values': [tgw]}])['TransitGatewayAttachments']

    # Fetch Cross Region TGWs
    cross_region_tgw_details = []
    for reg in ec2_client.describe_regions()['Regions']:
        cross_region_session = boto3.Session(region_name=reg['RegionName'])
        cross_region_ec2_client = cross_region_session.client('ec2')
        cross_region_tgws = cross_region_ec2_client.describe_transit_gateways()['TransitGateways']
        for tgw in cross_region_tgws:
            cross_region_tgw_details.append({'label': tgw['TransitGatewayId'], 'value': tgw['TransitGatewayId']})

    return eni_details, subnet_details, route_table_details, tgw_details, tgw_attachments, vpc_details, cross_region_tgw_details

def aws_network_graph(eni_details, subnet_details, route_table_details, tgw_details, tgw_attachments, vpc_details, cross_region_tgw_details):
    elements = []
    
import argparse
import boto3
import dash
from dash import html, dcc
from dash.dependencies import Input, Output
from dash_cytoscape import Cytoscape
import dash_mantine_components as dmc
import dash_bootstrap_components as dbc

def fetch_aws_data(account, region, ipv4, eni, subnet, route_table, destination_ipv4, tgw):
    session = boto3.Session(region_name=region)
    ec2_client = session.client('ec2')
    
    # Fetch VPCs
    vpcs = ec2_client.describe_vpcs()['Vpcs']
    vpc_details = [{'label': vpc['VpcId'], 'value': vpc['VpcId']} for vpc in vpcs]

    # Fetch ENIs
    eni_details = [{'label': eni['NetworkInterfaceId'], 'value': eni['NetworkInterfaceId']} for eni in ec2_client.describe_network_interfaces()['NetworkInterfaces']]

    # Fetch Subnets
    subnet_details = [{'label': subnet['SubnetId'], 'value': subnet['SubnetId']} for subnet in ec2_client.describe_subnets()['Subnets']]

    # Fetch Route Tables
    route_table_details = [{'label': rt['RouteTableId'], 'value': rt['RouteTableId']} for rt in ec2_client.describe_route_tables()['RouteTables']]

    # Fetch TGWs
    tgw_details = [{'label': tgw['TransitGatewayId'], 'value': tgw['TransitGatewayId']} for tgw in ec2_client.describe_transit_gateways()['TransitGateways']]

    # Fetch TGW Attachments
    tgw_attachments = ec2_client.describe_transit_gateway_attachments(Filters=[{'Name': 'transit-gateway-id', 'Values': [tgw]}])['TransitGatewayAttachments']

    # Fetch Cross Region TGWs
    cross_region_tgw_details = []
    for reg in ec2_client.describe_regions()['Regions']:
        cross_region_session = boto3.Session(region_name=reg['RegionName'])
        cross_region_ec2_client = cross_region_session.client('ec2')
        cross_region_tgws = cross_region_ec2_client.describe_transit_gateways()['TransitGateways']
        for tgw in cross_region_tgws:
            cross_region_tgw_details.append({'label': tgw['TransitGatewayId'], 'value': tgw['TransitGatewayId']})

    return eni_details, subnet_details, route_table_details, tgw_details, tgw_attachments, vpc_details, cross_region_tgw_details

def aws_network_graph(eni_details, subnet_details, route_table_details, tgw_details, tgw_attachments, vpc_details, cross_region_tgw_details):
    elements = []
    
    # Extracting data for local region
    vpc_id = vpc_details[0]["label"]
    eni_id = eni_details[0]["label"]
    subnet_id = subnet_details[0]["label"]
    route_table_id = route_table_details[0]["label"]
    tgw_id = tgw_details[0]["label"]
    tgw_attachment_id = tgw_attachments[0]["TransitGatewayAttachmentId"]
    tgw_route_table_id = tgw_attachments[0]['Association'].get('TransitGatewayRouteTableId')

    # Add nodes for local region
    elements.append({'data': {'id': 'eni', 'label': f'ENI {eni_id}', 'type': 'ENI'}})
    elements.append({'data': {'id': 'subnet', 'label': f'Subnet {subnet_id}', 'type': 'Subnet'}})
    elements.append({'data': {'id': 'route_table', 'label': f'Route Table {route_table_id}', 'type': 'Route Table'}})
    elements.append({'data': {'id': 'tgw', 'label': f'Transit Gateway {tgw_id}', 'type': 'Transit Gateway'}})
    elements.append({'data': {'id': 'vpc', 'label': f'VPC {vpc_id}', 'type': 'VPC'}})
    elements.append({'data': {'id': 'tgw_rtb', 'label': f'Tgw Route Table ID {tgw_route_table_id}', 'type': 'Tgw Route Table ID'}})
    elements.append({'data': {'id': 'tgw_attachment', 'label': f'Transit Gateway Attachment {tgw_attachment_id}', 'type': 'Transit Gateway Attachment'}})

    # Add edges for local region
    elements.append({'data': {'source': 'eni', 'target': 'subnet'}})
    elements.append({'data': {'source': 'subnet', 'target': 'route_table'}})
    elements.append({'data': {'source': 'route_table', 'target': 'tgw'}})
    elements.append({'data': {'source': 'tgw', 'target': 'vpc'}})
    elements.append({'data': {'source': 'vpc', 'target': 'tgw_rtb'}})
    elements.append({'data': {'source': 'tgw_rtb', 'target': 'tgw_attachment'}})

    # Extracting data for cross region TGWs
    for cross_region_tgw in cross_region_tgw_details:
        cross_region_tgw_id = cross_region_tgw["label"]
        elements.append({'data': {'id': f'cross_region_tgw_{cross_region_tgw_id}', 'label': f'Cross Region TGW {cross_region_tgw_id}', 'type': 'Cross Region TGW'}})

    app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
    app.layout = dbc.Container([
        dbc.Row([dbc.Col(html.H3("AWS Network Graph"), className="mb-4")]),
        dbc.Row([dbc.Col(
            Cytoscape(
                id='graph',
                layout={'name': 'grid'},
                style={'width': '100%', 'height': '800px'},
                elements=elements,
                stylesheet=[
                    {'selector': 'node', 'style': {'content': 'data(label)', 'font-size': '12px', 'width': '70px', 'height': '70px', 'shape': 'ellipse', 'text-halign': 'center', 'text-valign': 'bottom'}},
                    {'selector': 'edge', 'style': {'width': 2, 'line-color': '#9DB5B2', 'curve-style': 'bezier', 'line-color': '#2a2b28', 'target-arrow-color': '#2a2b28', 'target-arrow-shape': 'triangle'}},
                ],
            ), width=12
        )]),
        dbc.Row([dbc.Col(html.Div(id='node-info', className="mt-4"))])
    ])

    @app.callback(Output('node-info', 'children'), [Input('graph', 'tapNode')])
    def display_node_data(tap_node):
        if tap_node:
            node_id = tap_node['data']['id']
            node_type = tap_node['data']['type']
            node_info = f"Information about {node_type}:\n"
            if node_type == 'VPC':
                node_info += f"- VPC ID: {vpc_id}\n"
            # Add more information for other node types as needed
            return dcc.Markdown(node_info)
        return None

    app.run_server(debug=True)

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

    aws_data = fetch_aws_data(args.account, args.region, args.ipv4, args.eni, args.subnet, args.route_table, args.destination_ipv4, args.tgw)
    aws_network_graph(*aws_data)
￼Enter
