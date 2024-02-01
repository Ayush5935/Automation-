import argparse
import boto3
import dash
from dash import html, dcc
from dash.dependencies import Input, Output
from dash_cytoscape import Cytoscape
import dash_mantine_components as dmc
import dash_bootstrap_components as dbc

def fetch_aws_data(account, region, ipv4, eni, subnet, route_table, destination_ipv4, tgw):
    # Your existing code for fetching AWS data

def aws_network_graph(eni_details, subnet_details, route_table_details, tgw_details, tgw_attachments_details):
    elements = []

    color_mapping = {
        'ENI': '#6FB1FC',  # Blue
        'Subnet': '#98FB98',  # Green
        'Route Table': '#FFD700',  # Yellow
        'Transit Gateway': '#FF6347',  # Red
        'Transit Gateway Attachment': '#8A2BE2',  # Purple
    }

    shape_mapping = {
        'ENI': 'ellipse',
        'Subnet': 'roundrectangle',
        'Route Table': 'rectangle',
        'Transit Gateway': 'pentagon',
        'Transit Gateway Attachment': 'hexagon',
    }

    size_mapping = {
        'ENI': 40,
        'Subnet': 50,
        'Route Table': 60,
        'Transit Gateway': 70,
        'Transit Gateway Attachment': 80,
    }

    for details_list in [eni_details, subnet_details, route_table_details, tgw_details, tgw_attachments_details]:
        for details in details_list:
            node_type = details.get('details', {}).get('type', 'Other')
            node_id = f"{node_type}_{details['label']}"
            elements.append({
                'data': {
                    'id': node_id,
                    'label': f"{node_type} {details['label']}",
                    'info': details,
                    'color': color_mapping.get(node_type, 'gray'),
                    'shape': shape_mapping.get(node_type, 'ellipse'),
                    'width': size_mapping.get(node_type, 60),
                    'height': size_mapping.get(node_type, 60),
                }
            })

    for link in [('ENI', 'Subnet'), ('Subnet', 'Route Table'), ('Route Table', 'Transit Gateway'), ('Transit Gateway', 'Transit Gateway Attachment'), ('Transit Gateway Attachment', 'TGW RTB')]:
        elements.append({'data': {'source': f"{link[0]}_{eni_details[0]['label']}", 'target': f"{link[1]}_{subnet_details[0]['label']}"}})

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
                        {
                            'selector': 'node',
                            'style': {
                                'content': 'data(label)',
                                'font-size': '12px',
                                'width': 'data(width)',
                                'height': 'data(height)',
                                'shape': 'data(shape)',
                                'background-color': 'data(color)',
                                'border-color': '#3573A5',
                                'text-halign': 'center',
                                'text-valign': 'bottom',
                            }
                        },
                        {
                            'selector': 'edge',
                            'style': {
                                'width': 3,
                                'line-color': '#9DB5B2',
                                'curve-style': 'bezier',
                                'target-arrow-shape': 'triangle'
                            }
                        }
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
        [Input('graph', 'tapNode'), Input('graph', 'selectNodeData')]
    )
    def display_node_data(tap_node, selected_node_data):
        if tap_node:
            node_id = tap_node['data']['id']
        elif selected_node_data:
            node_id = selected_node_data[0]['id']
        else:
            return None

        node_info = f"Information about {node_id}:\n - ENI {eni_id} \n - Account {args.account} \n - Region {args.region} \n - IPv4 {args.ipv4}"
        return dcc.Markdown(node_info)

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
