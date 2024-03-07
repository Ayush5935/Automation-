import argparse
import boto3
import dash
from dash import html, dcc
from dash.dependencies import Input, Output
from dash_cytoscape import Cytoscape
import dash_mantine_components as dmc
import dash_bootstrap_components as dbc

def fetch_aws_data(account, region, source_ip, destination_ip):
    session = boto3.Session(region_name=region)

    ec2_client = session.client('ec2')
    
    # Fetch ENI ID based on source IP
    eni_response = ec2_client.describe_network_interfaces(Filters=[{'Name': 'private-ip-address', 'Values': [source_ip]}])
    eni_id = eni_response['NetworkInterfaces'][0]['NetworkInterfaceId']
    
    # Fetch Subnet ID from ENI
    subnet_id = eni_response['NetworkInterfaces'][0]['SubnetId']
    
    # Fetch VPC ID from Subnet
    subnet_response = ec2_client.describe_subnets(SubnetIds=[subnet_id])
    vpc_id = subnet_response['Subnets'][0]['VpcId']
    
    # Fetch Route Table ID
    route_table_response = ec2_client.describe_route_tables(Filters=[{'Name': 'vpc-id', 'Values': [vpc_id]}])
    route_table_id = route_table_response['RouteTables'][0]['RouteTableId']
    
    # Fetch TGW ID from routes
    tgw_id = None
    routes = route_table_response['RouteTables'][0]['Routes']
    for route in routes:
        if 'TransitGatewayId' in route:
            tgw_id = route['TransitGatewayId']
            break
    
    # Fetch TGW Attachment and TGW Route Table (Association Route Table)
    tgw_attachments = ec2_client.describe_transit_gateway_attachments(Filters=[{'Name': 'transit-gateway-id', 'Values': [tgw_id]}, {'Name': 'vpc-id', 'Values': [vpc_id]}])['TransitGatewayAttachments']
    tgw_attachment = tgw_attachments[0]['TransitGatewayAttachmentId'] if tgw_attachments else None
    tgw_association_route_table = tgw_attachments[0]['Association']['TransitGatewayRouteTableId'] if tgw_attachments else None
    
    return eni_id, subnet_id, vpc_id, route_table_id, tgw_id, tgw_attachment, tgw_association_route_table

def aws_network_graph(eni_id, subnet_id, vpc_id, route_table_id, tgw_id, tgw_attachment, tgw_association_route_table):
    elements = []

    elements.append({'data': {'id': 'eni', 'label': f'ENI  {eni_id}', 'type':'ENI'}})
    elements.append({'data': {'id': 'subnet', 'label': f'Subnet  {subnet_id}','type':'Subnet'}})
    elements.append({'data': {'id': 'route_table', 'label': f'Route Table  {route_table_id}','type':'Route Table'}})
    elements.append({'data': {'id': 'tgw', 'label': f'Transit Gateway {tgw_id}','type':'Transit Gateway'}})
    elements.append({'data': {'id': 'vpc', 'label': f'VPC  {vpc_id}', 'type':'VPC'}})
    elements.append({'data': {'id': 'tgw_attachment', 'label': f'Transit Gateway Attachment {tgw_attachment}','type':'Transit Gateway Attachment'}})
    elements.append({'data': {'id': 'tgw_association_route_table', 'label': f'TGW Association Route Table {tgw_association_route_table}','type':'TGW Association Route Table'}})

    elements.append({'data': {'source': 'eni', 'target': 'subnet'}})
    elements.append({'data': {'source': 'subnet', 'target': 'route_table'}})
    elements.append({'data': {'source': 'route_table', 'target': 'tgw'}})
    elements.append({'data': {'source': 'tgw', 'target': 'vpc'}})
    elements.append({'data': {'source': 'vpc', 'target': 'tgw_attachment'}})
    elements.append({'data': {'source': 'tgw_attachment', 'target': 'tgw_association_route_table'}})

    app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

    app.layout = dbc.Container([
        dbc.Row([
            dbc.Col(html.H3("AWS Network Graph"),className="mb-4")
        ]),
        dbc.Row([
            dbc.Col(
                Cytoscape(
                    id='graph',
                    layout={'name': 'grid'},
                    style={'width': '100%', 'height': '800px'},
                    elements=elements,
                    stylesheet = [
                        # Add your stylesheet here
                    ]
                ),
                width=12
            )
        ]),
        dbc.Row([
            dbc.Col(
                html.Div(id='node-info', className="mt-4")
            )
        ])
    ])

    @app.callback(
        Output('node-info', 'children'),
        [Input('graph', 'tapNode')]
    )

    def display_node_data(tap_node):
        if tap_node:
            node_id = tap_node['data']['id']
            node_type = tap_node['data']['type']
            node_info = f"Information about {node_type}:\n"

            # Add node information based on type

            return dcc.Markdown(node_info)
        return None

    app.run_server(debug=True)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate and visualize AWS network graph.')
    parser.add_argument('--account', help='AWS account ID', required=True)
    parser.add_argument('--region', help='AWS region', required=True)
    parser.add_argument('--source-ip', help='Source Private IP', required=True)
    parser.add_argument('--destination-ip', help='Destination Private IP', required=True)
    args = parser.parse_args()

    aws_data = fetch_aws_data(args.account, args.region, args.source_ip, args.destination_ip)
    aws_network_graph(*aws_data)
