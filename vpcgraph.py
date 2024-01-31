import dash
from dash import html
from dash_cytoscape import Cytoscape
import boto3
import argparse

def generate_aws_network_graph(account_id, region):
    # Connect to AWS using Boto3
    session = boto3.Session(
        aws_access_key_id='your_access_key',
        aws_secret_access_key='your_secret_key',
        region_name=region
    )
    
    ec2_client = session.client('ec2')

    # Fetch VPCs
    vpcs = ec2_client.describe_vpcs()['Vpcs']

    elements = []

    for vpc in vpcs:
        vpc_id = vpc['VpcId']
        elements.append({'data': {'id': vpc_id, 'label': f'VPC {vpc_id}'}})

        # Fetch Subnets
        subnets = ec2_client.describe_subnets(Filters=[{'Name': 'vpc-id', 'Values': [vpc_id]}])['Subnets']
        for subnet in subnets:
            subnet_id = subnet['SubnetId']
            elements.append({'data': {'id': subnet_id, 'label': f'Subnet {subnet_id}'}})
            elements.append({'data': {'source': vpc_id, 'target': subnet_id}})

        # Fetch Route Tables
        route_tables = ec2_client.describe_route_tables(Filters=[{'Name': 'vpc-id', 'Values': [vpc_id]}])['RouteTables']
        for route_table in route_tables:
            route_table_id = route_table['RouteTableId']
            elements.append({'data': {'id': route_table_id, 'label': f'Route Table {route_table_id}'}})
            elements.append({'data': {'source': vpc_id, 'target': route_table_id}})

            # Fetch Route Table Entries
            for route in route_table['Routes']:
                destination_cidr = route.get('DestinationCidrBlock', '')
                if destination_cidr:
                    elements.append({'data': {'id': destination_cidr, 'label': f'Destination: {destination_cidr}'}})
                    elements.append({'data': {'source': route_table_id, 'target': destination_cidr}})

            # Fetch Route Table Associations (Subnets)
            associations = route_table.get('Associations', [])
            for association in associations:
                subnet_id = association.get('SubnetId', '')
                if subnet_id:
                    elements.append({'data': {'source': subnet_id, 'target': route_table_id}})

            # Fetch Route Table Attachments (Transit Gateway)
            attachments = route_table.get('Associations', [])
            for attachment in attachments:
                attachment_id = attachment.get('TransitGatewayAttachmentId', '')
                if attachment_id:
                    elements.append({'data': {'id': attachment_id, 'label': f'Attachment {attachment_id}'}})
                    elements.append({'data': {'source': vpc_id, 'target': attachment_id}})

    return elements

def create_dash_app(elements):
    # Create the Dash app
    app = dash.Dash(__name__)

    # Define the layout
    app.layout = html.Div([
        Cytoscape(
            id='graph',
            layout={'name': 'circle'},
            style={'width': '100%', 'height': '600px'},
            elements=elements,
            stylesheet=[
                {
                    'selector': 'node',
                    'style': {
                        'content': 'data(label)',
                        'background-fit': 'cover',
                        'background-color': '#ffffff',
                        'border-color': '#3573A5',
                        'border-width': 2,
                        'font-size': '12px',
                        'width': '100px',
                        'height': '100px',
                    }
                },
                {
                    'selector': 'edge',
                    'style': {
                        'width': 3,
                        'line-color': '#9DB5B2',
                        'curve-style': 'bezier'
                    }
                }
            ]
        )
    ])

    return app

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate and visualize AWS network graph.')
    parser.add_argument('--account', help='AWS account ID', required=True)
    parser.add_argument('--region', help='AWS region', required=True)
    args = parser.parse_args()

    graph_elements = generate_aws_network_graph(account_id=args.account, region=args.region)
    app = create_dash_app(graph_elements)
    app.run_server(debug=True)
