import argparse
import boto3
import dash
from dash import html, dcc
from dash.dependencies import Input, Output
from dash_cytoscape import Cytoscape
import dash_bootstrap_components as dbc
from dash_iconify import DashIconify

def fetch_aws_data(account, region, ipv4, eni, subnet, route_table, destination_ipv4, tgw):
    # (Your existing code for fetching AWS data)

def aws_network_graph(eni_details, subnet_details, route_table_details, tgw_details, tgw_attachments):
    elements = []
    eni_id = eni_details[0]["label"]
    subnet_id = subnet_details[0]["label"]
    route_table_id = route_table_details[0]["label"]
    tgw_id = tgw_details[0]["label"]
    tgw_attachment_id = tgw_attachments[0]["TransitGatewayAttachmentId"]
    tgw_route_table_id = tgw_attachments[0]['Association'].get('TransitGatewayRouteTableId')

    elements.append({'data': {'id': 'eni', 'label': f'ENI {eni_id}', 'type': 'ENI', 'icon': 'https://img.icons8.com/ios-filled/50/000000/aws.png'}})
    elements.append({'data': {'id': 'subnet', 'label': f'Subnet {subnet_id}'}})
    elements.append({'data': {'id': 'route_table', 'label': f'Route Table {route_table_id}'}})
    elements.append({'data': {'id': 'tgw', 'label': f'Transit Gateway {tgw_id}'}})
    elements.append({'data': {'id': 'tgw_rtb', 'label': f'Tgw Route Table ID {tgw_route_table_id}'}})
    elements.append({'data': {'id': 'tgw_attachment', 'label': f'Transit Gateway Attachment {tgw_attachment_id}'}})
    elements.append({'data': {'source': 'eni', 'target': 'subnet'}})
    elements.append({'data': {'source': 'subnet', 'target': 'route_table'}})
    elements.append({'data': {'source': 'route_table', 'target': 'tgw'}})
    elements.append({'data': {'source': 'tgw', 'target': 'tgw_attachment'}})
    elements.append({'data': {'source': 'tgw_attachment', 'target': 'tgw_rtb'}})

    app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

    app.layout = dbc.Container([
        dbc.Row([
            dbc.Col(html.H1("AWS Network Graph"), className="mb-4")
        ]),
        dbc.Row([
            dbc.Col(
                Cytoscape(
                    id='graph',
                    layout={'name': 'circle'},
                    style={'width': '100%', 'height': '600px'},
                    elements=elements,
                    stylesheet=[
                        {'selector': 'node', 'style': {'content': 'data(label)', 'font-size': '12px', 'width': '90px', 'height': '90px', 'shape': 'ellipse', 'text-halign': 'center', 'text-valign': 'bottom'}},
                        {'selector': '#eni', 'style': {'background-image': 'url(https://img.icons8.com/ios-filled/50/000000/aws.png)', 'background-fit': 'cover', 'background-width': '70%', 'background-height': '70%', 'border-color': '#3573A5'}},
                        {'selector': '#subnet', 'style': {'background-color': '#98FB98', 'border-color': '#4CAF50'}},
                        {'selector': '#route_table', 'style': {'background-color': '#FFD700', 'border-color': '#FFC107'}},
                        {'selector': '#tgw', 'style': {'background-color': '#FF6347', 'border-color': '#E57373'}},
                        {'selector': '#tgw_attachment', 'style': {'background-color': '#8A2BE2', 'border-color': '#7B1FA2'}},
                        {'selector': '#tgw_rtb', 'style': {'background-color': '#30c8d9', 'border-color': '#30c8d9'}},
                        {'selector': 'edge', 'style': {'width': 3, 'line-color': '#9DB5B2', 'curve-style': 'bezier', 'target-arrow-shape': 'triangle'}}
                    ]
                ),
                width=12
            )
        ]),
        dbc.Row([
            dbc.Col(
                DashIconify(
                    icon="ion:logo-github",
                    width=30,
                    rotate=1,
                    flip="horizontal",
                ),
                className="mt-4"
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
            node_info = f"Information about {node_id}:\n - ENI {eni_id} \n - Account {args.account} \n - Region {args.region} \n - IPv4 {args.ipv4}"
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
