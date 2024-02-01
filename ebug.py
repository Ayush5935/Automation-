def aws_network_graph(eni_details, subnet_details, route_table_details, tgw_details, tgw_attachments_details):
    elements = []

    for details_list in [eni_details, subnet_details, route_table_details, tgw_details, tgw_attachments_details]:
        for details in details_list:
            node_type = details.get('details', {}).get('type', 'Other')
            node_id = f"{node_type}_{details['label']}"
            elements.append({'data': {'id': node_id, 'label': f"{node_type} {details['label']}"}})

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
                                'width': '90px',
                                'height': '90px',
                                'shape': 'ellipse',
                                'text-halign': 'center',
                                'text-valign': 'bottom',
                                'background-color': 'gray',
                                'border-color': 'black',
                                'border-width': 2,
                            }
                        },
                        {
                            'selector': 'edge',
                            'style': {
                                'width': 3,
                                'line-color': '#9DB5B2',
                                'curve-style': 'bezier',
                                'target-arrow-shape': 'triangle',
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
