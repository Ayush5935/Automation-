import argparse
import boto3
import dash
from dash import html, dcc
from dash.dependencies import Input, Output
from dash_cytoscape import Cytoscape

def fetch_aws_data(account, region, ipv4, eni, subnet, route_table, destination_ipv4, tgw):
    session = boto3.Session(region_name=region)
    ec2_client = session.client('ec2')

    eni_details = [{'label': eni['NetworkInterfaceId'], 'value': eni['NetworkInterfaceId'], 'type': 'ENI', 'details': eni} for eni in ec2_client.describe_network_interfaces()['NetworkInterfaces']]
    subnet_details = [{'label': subnet['SubnetId'], 'value': subnet['SubnetId'], 'type': 'Subnet', 'details': subnet} for subnet in ec2_client.describe_subnets()['Subnets']]
    route_table_details = [{'label': rt['RouteTableId'], 'value': rt['RouteTableId'], 'type': 'Route Table', 'details': rt} for rt in ec2_client.describe_route_tables()['RouteTables']]
    tgw_details = [{'label': tgw['TransitGatewayId'], 'value': tgw['TransitGatewayId'], 'type': 'Transit Gateway', 'details': tgw} for tgw in ec2_client.describe_transit_gateways()['TransitGateways']]
    
    tgw_attachments = ec2_client.describe_transit_gateway_attachments(Filters=[{'Name': 'transit-gateway-id', 'Values': [tgw]}])['TransitGatewayAttachments']
    tgw_attachments_details = [{'label': attachment['TransitGatewayAttachmentId'], 'value': attachment['TransitGatewayAttachmentId'], 'type': 'Transit Gateway Attachment', 'details': attachment} for attachment in tgw_attachments]

    return eni_details, subnet_details, route_table_details, tgw_details, tgw_attachments_details

def aws_network_graph(eni_details, subnet_details, route_table_details, tgw_details, tgw_attachments_details):
    elements = []

    for details_list in [eni_details, subnet_details, route_table_details, tgw_details, tgw_attachments_details]:
        for details in details_list:
            node_id = f"{details['type']}_{details['label']}"
            elements.append({'data': {'id': node_id, 'label': f"{details['type']} {details['label']}", 'info': details}})

    for link in [('eni', 'subnet'), ('subnet', 'route_table'), ('route_table', 'tgw'), ('tgw', 'tgw_attachment'), ('tgw_attachment', 'tgw_rtb')]:
        elements.append({'data': {'source': link[0], 'target': link[1]}})

    app = dash.Dash(__name__)

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
                        'font-size': '12px',
                        'width': '100px',
                        'height': '100px',
                        'shape': 'ellipse',
                        'text-halign': 'center',
                        'text-valign': 'center',
                    }
                },
                {
                    'selector': '[type = "ENI"]',
                    'style': {
                        'background-color': '#6FB1FC',  # Blue
                        'border-color': '#3573A5',
                    }
                },
                {
                    'selector': '[type = "Subnet"]',
                    'style': {
                        'background-color': '#98FB98',  # Green
                        'border-color': '#4CAF50',
                    }
                },
                {
                    'selector': '[type = "Route Table"]',
                    'style': {
                        'background-color': '#FFD700',  # Yellow
                        'border-color': '#FFC107',
                    }
                },
                {
                    'selector': '[type = "Transit Gateway"]',
                    'style': {
                        'background-color': '#FF6347',  # Red
                        'border-color': '#E57373',
                    }
                },
                {
                    'selector': '[type = "Transit Gateway Attachment"]',
                    'style': {
                        'background-color': '#8A2BE2',  # Purple
                        'border-color': '#7B1FA2',
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

    # Add callback to update the node information on click
    @app.callback(
        Output('node-info', 'children'),
        [Input('graph', 'tapNode')]
    )
    def display_node_data(tap_node):
        if tap_node:
            node_id = tap_node['data']['id']
            node_info = tap_node['data'].get('info')

            if node_info:
                formatted_info = "\n".join([f"{key}: {value}" for key, value in node_info['details'].items()])
                return dcc.Markdown(f"Information about {node_id}:\n{formatted_info}")

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
