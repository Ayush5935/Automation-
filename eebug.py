import argparse
import boto3
import dash
from dash import html
from dash_cytoscape import Cytoscape

def fetch_aws_data(account, region, ipv4, eni, subnet, route_table, destination_ipv4, tgw):
    session = boto3.Session(region_name=region)
    ec2_client = session.client('ec2')

    eni_details = [{'label': eni['NetworkInterfaceId'], 'value': eni['NetworkInterfaceId']} for eni in ec2_client.describe_network_interfaces()['NetworkInterfaces']]
    subnet_details = [{'label': subnet['SubnetId'], 'value': subnet['SubnetId']} for subnet in ec2_client.describe_subnets()['Subnets']]
    route_table_details = [{'label': rt['RouteTableId'], 'value': rt['RouteTableId']} for rt in ec2_client.describe_route_tables()['RouteTables']]
    tgw_details = [{'label': tgw['TransitGatewayId'], 'value': tgw['TransitGatewayId']} for tgw in ec2_client.describe_transit_gateways()['TransitGateways']]
    tgw_attachments = ec2_client.describe_transit_gateway_attachments(Filters=[{'Name': 'transit-gateway-id', 'Values': [tgw]}])['TransitGatewayAttachments']

    return eni_details, subnet_details, route_table_details, tgw_details, tgw_attachments

def aws_network_graph(eni_details, subnet_details, route_table_details, tgw_details, tgw_attachments):
    elements = []

    elements.append({'data': {'id': 'eni', 'label': 'ENI'}})
    elements.append({'data': {'id': 'subnet', 'label': 'Subnet'}})
    elements.append({'data': {'id': 'route_table', 'label': 'Route Table'}})
    elements.append({'data': {'id': 'tgw', 'label': 'Transit Gateway'}})

    for subnet in subnet_details:
        subnet_id = subnet['value']
        elements.append({'data': {'id': subnet_id, 'label': f'Subnet\n{subnet_id}'}})
        elements.append({'data': {'source': 'eni', 'target': subnet_id}})
    
    for route_table in route_table_details:
        rt_id = route_table['value']
        elements.append({'data': {'id': rt_id, 'label': f'Route Table\n{rt_id}'}})
        elements.append({'data': {'source': 'subnet', 'target': rt_id}})
    
    for tgw in tgw_details:
        tgw_id = tgw['value']
        elements.append({'data': {'id': tgw_id, 'label': f'Transit Gateway\n{tgw_id}'}})
        elements.append({'data': {'source': 'route_table', 'target': tgw_id}})
    
    for attachment in tgw_attachments:
        attachment_id = attachment['TransitGatewayAttachmentId']
        elements.append({'data': {'id': attachment_id, 'label': f'Attachment\n{attachment_id}'}})
        elements.append({'data': {'source': 'tgw', 'target': attachment_id}})
        
        # Extract Transit Gateway Route Table ID from Attachment
        tgw_route_table_id = attachment.get('Association', {}).get('TransitGatewayRouteTableId', '')
        if tgw_route_table_id:
            elements.append({'data': {'id': tgw_route_table_id, 'label': f'TGW Route Table\n{tgw_route_table_id}'}})
            elements.append({'data': {'source': attachment_id, 'target': tgw_route_table_id}})
    
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
                        'background-color': '#6FB1FC',
                        'border-color': '#3573A5',
                        'border-width': 2,
                        'font-size': '12px',
                        'width': '50px',
                        'height': '50px',
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
