import argparse
import boto3
import dash
from dash import html, dcc
from dash.dependencies import Input, Output
from dash_cytoscape import Cytoscape
import dash_mantine_components as dmc
import dash_bootstrap_components as dbc

def fetch_aws_data(account, region, ipv4, eni, subnet, route_table, destination_ipv4, tgw):
    # ... (Your existing function remains unchanged)

def aws_network_graph(eni_details, subnet_details, route_table_details, tgw_details, tgw_attachments):
    elements = []
    eni_id = eni_details[0]["label"]
    subnet_id = subnet_details[0]["label"]
    route_table_id = route_table_details[0]["label"]
    tgw_id = tgw_details[0]["label"]
    tgw_attachment_id = tgw_attachments[0]["TransitGatewayAttachmentId"]
    tgw_route_table_id = tgw_attachments[0]['Association'].get('TransitGatewayRouteTableId')

    elements.append({'data': {'id': 'eni', 'label': f'ENI {eni_id}', 'type': 'ENI', 'icon': 'https://fontawesome.com/icons/user?f=classic&s=solid'}})
    elements.append({'data': {'id': 'subnet', 'label': f'Subnet {subnet_id}', 'type': 'Subnet', 'icon': 'https://fontawesome.com/icons/network-wired?f=classic&s=solid'}})
    elements.append({'data': {'id': 'route_table', 'label': f'Route Table {route_table_id}', 'type': 'Route Table', 'icon': 'https://fontawesome.com/icons/project-diagram?f=classic&s=solid'}})
    elements.append({'data': {'id': 'tgw', 'label': f'Transit Gateway {tgw_id}', 'type': 'Transit Gateway', 'icon': 'https://fontawesome.com/icons/network-wired?f=classic&s=solid'}})
    elements.append({'data': {'id': 'tgw_rtb', 'label': f'Tgw Route Table ID {tgw_route_table_id}', 'type': 'Transit Gateway Attachment', 'icon': 'https://fontawesome.com/icons/link?f=classic&s=solid'}})
    elements.append({'data': {'id': 'tgw_attachment', 'label': f'Transit Gateway Attachment {tgw_attachment_id}', 'type': 'Transit Gateway Attachment', 'icon': 'https://fontawesome.com/icons/link?f=classic&s=solid'}})
    elements.append({'data': {'source': 'eni', 'target': 'subnet'}})
    elements.append({'data': {'source': 'subnet', 'target': 'route_table'}})
    elements.append({'data': {'source': 'route_table', 'target': 'tgw'}})
    elements.append({'data': {'source': 'tgw', 'target': 'tgw_attachment'}})
    elements.append({'data': {'source': 'tgw_attachment', 'target': 'tgw_rtb'}})

    app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])
    app.layout = dbc.Container([
        dbc.Row([
            dbc.Col(html.H1("AWS Network Graph"), className="mb-4")
        ]),
        dbc.Row([
            dbc.Col(
                Cytoscape(
                    id='graph',
                    layout={'name': 'grid'},  # Use 'grid' for a straight-line layout
                    style={'width': '100%', 'height': '600px'},
                    elements=elements,
                    stylesheet=[
                        {
                            'selector': 'node',
                            'style': {
                                'content': 'data(label)',
                                'font-size': '12px',
                                'width': '90px',
                                'height': '90px',
                                'shape': 'ellipse',
                                'text-halign': 'center',
                                'text-valign': 'bottom',
                            },
                        },
                        {
                            'selector': '[type = "ENI"]',
                            'style': {
                                'background-image': 'url(https://fontawesome.com/icons/user?f=classic&s=solid)',
                                'background-fit': 'cover',
                                'background-width': '70%',
                                'background-height': '70%',
                            },
                        },
                        {
                            'selector': '[type = "Subnet"]',
                            'style': {
                                'background-image': 'url(https://fontawesome.com/icons/network-wired?f=classic&s=solid)',
                                'background-fit': 'cover',
                                'background-width': '80%',
                                'background-height': '80%',
                            },
                        },
                        {
                            'selector': '[type = "Route Table"]',
                            'style': {
                                'background-image': 'url(https://fontawesome.com/icons/project-diagram?f=classic&s=solid)',
                                'background-fit': 'cover',
                                'background-width': '80%',
                                'background-height': '80%',
                            },
                        },
                        {
                            'selector': '[type = "Transit Gateway"]',
                            'style': {
                                'background-image': 'url(https://fontawesome.com/icons/network-wired?f=classic&s=solid)',
                                'background-fit': 'cover',
                                'background-width': '80%',
                                'background-height': '80%',
                            },
                        },
                        {
                            'selector': '[type = "Transit Gateway Attachment"]',
                            'style': {
                                'background-image': 'url(https://fontawesome.com/icons/link?f=classic&s=solid)',
                                'background-fit': 'cover',
                                'background-width': '80%',
                                'background-height': '80%',
                            },
                        },
                        {
                            'selector': 'edge',
                            'style': {
                                'width': 3,
                                'line-color': '#9DB5B2',
                                'curve-style': 'bezier',
                                'target-arrow-shape': 'triangle',
                            },
                        },
                    ],
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
            node_info = f"Information about {node_id}:\n - ENI {eni_id} \n - Account {args.account} \n - Region {args.region} \n - IPv4 {args.ipv4}"
            return dcc.Markdown(node_info)
        return None

    app.run_server(debug=True)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate and visualize AWS network graph.')
    # ... (Your existing argument parsing remains unchanged)
    args = parser.parse_args()
    aws_data = fetch_aws_data(args.account, args.region, args.ipv4, args.eni, args.subnet, args.route_table, args.destination_ipv4, args.tgw)
    aws_network_graph(*aws_data)
