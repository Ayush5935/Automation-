def generate_aws_network_graph(eni_details, subnet_details, route_table_details, tgw_details, tgw_attachments):
    # Logic to process fetched data and generate graph using Dash Cytoscape
    elements = []

    # Extracting details for nodes
    eni_id = eni_details[0]['NetworkInterfaceId'] if eni_details else ''
    
    if subnet_details and 'Subnets' in subnet_details:
        subnet_id = subnet_details['Subnets'][0]['SubnetId'] if subnet_details['Subnets'] else ''
    else:
        subnet_id = ''
    
    if route_table_details and 'RouteTables' in route_table_details:
        route_table_id = route_table_details['RouteTables'][0]['RouteTableId'] if route_table_details['RouteTables'] else ''
    else:
        route_table_id = ''
    
    destination_ipv4 = 'Destination\n'  # Add your logic to fetch the destination IPv4

    if tgw_details and 'TransitGateways' in tgw_details:
        tgw_id = tgw_details['TransitGateways'][0]['TransitGatewayId'] if tgw_details['TransitGateways'] else ''
        
        # Add Transit Gateway as a node
        elements.append({'data': {'id': 'tgw', 'label': f'Transit Gateway\n{tgw_id}'}})
        
        # Add Transit Gateway attachments as separate nodes
        for attachment in tgw_attachments:
            attachment_id = attachment.get('TransitGatewayAttachmentId', '')
            elements.append({'data': {'id': attachment_id, 'label': f'Attachment\n{attachment_id}'}})
            elements.append({'data': {'source': 'tgw', 'target': attachment_id}})
    else:
        tgw_id = ''

    # Example: Add nodes and edges based on fetched data
    elements.append({'data': {'id': 'source', 'label': 'Source'}})
    elements.append({'data': {'id': 'eni', 'label': f'ENI\n{eni_id}'}})
    elements.append({'data': {'id': 'subnet', 'label': f'Subnet\n{subnet_id}'}})
    elements.append({'data': {'id': 'route_table', 'label': f'Route Table\n{route_table_id}'}})
    elements.append({'data': {'id': 'destination', 'label': destination_ipv4}})

    # Add edges based on the availability of data
    if eni_id:
        elements.append({'data': {'source': 'source', 'target': 'eni'}})

    if subnet_id:
        elements.append({'data': {'source': 'eni', 'target': 'subnet'}})

    if route_table_id:
        elements.append({'data': {'source': 'subnet', 'target': 'route_table'}})
        elements.append({'data': {'source': 'route_table', 'target': 'destination'}})

    if tgw_id:
        elements.append({'data': {'source': 'route_table', 'target': 'tgw'}})

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
                        'background-color': '#6FB1FC',
                        'border-color': '#3573A5',
                        'border-width': 2,
                        'font-size': '12px',
                        'width': '100px',
                        'height': '50px',
                        'text-valign': 'center',
                        'text-halign': 'center',
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
    generate_aws_network_graph(*aws_data)
