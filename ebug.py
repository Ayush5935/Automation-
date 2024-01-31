import argparse
import boto3
import dash
from dash import html
from dash_cytoscape import Cytoscape

def fetch_aws_data(account, region, ipv4, eni, subnet, route_table, destination_ipv4, tgw):
    # Your existing function to fetch AWS data
    # ...

def aws_network_graph(eni_details, subnet_details, route_table_details, tgw_details, tgw_attachments):
    elements = []

    # Add nodes with unique IDs
    eni_id = eni_details[0]["label"]
    subnet_id = subnet_details[0]["label"]
    route_table_id = route_table_details[0]["label"]
    tgw_id = tgw_details[0]["label"]
    tgw_attachment_id = tgw_attachments[0]["TransitGatewayAttachmentId"]

    elements.append({'data': {'id': 'eni', 'label': f'ENI\n{eni_id}'}})
    elements.append({'data': {'id': 'subnet', 'label': f'Subnet\n{subnet_id}'}})
    elements.append({'data': {'id': 'route_table', 'label': f'Route Table\n{route_table_id}'}})
    elements.append({'data': {'id': 'tgw', 'label': f'Transit Gateway\n{tgw_id}'}})
    elements.append({'data': {'id': 'tgw_rtb', 'label': f'{tgw_id} Route Table\n{tgw_id}-rtb-079xx'}})
    elements.append({'data': {'id': 'tgw_attachment', 'label': f'Transit Gateway Attachment\n{tgw_attachment_id}'}})

    elements.append({'data': {'source': 'eni', 'target': 'subnet'}})
    elements.append({'data': {'source': 'subnet', 'target': 'route_table'}})
    elements.append({'data': {'source': 'route_table', 'target': 'tgw'}})
    elements.append({'data': {'source': 'tgw', 'target': 'tgw_attachment'}})
    elements.append({'data': {'source': 'tgw_attachment', 'target': 'tgw_rtb'}})

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
                        'width': '100px',
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
