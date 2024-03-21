def fetch_aws_data(account, region, ipv4, eni):
    session = boto3.Session(region_name=region)
    ec2_client = session.client('ec2')

    # Fetch ENI details
    eni_details = ec2_client.describe_network_interfaces(
        NetworkInterfaceIds=[eni]
    )['NetworkInterfaces'][0]

    # Get Security Group IDs associated with the ENI
    security_group_ids = eni_details['Groups']

    # Fetch Security Group details and rules
    security_groups = []
    for sg_id in security_group_ids:
        sg_details = ec2_client.describe_security_groups(
            GroupIds=[sg_id['GroupId']]
        )['SecurityGroups'][0]
        sg_rules = ec2_client.describe_security_group_rules(
            GroupId=sg_id['GroupId']
        )['SecurityGroupRules']
        security_groups.append({'details': sg_details, 'rules': sg_rules})

    return {
        'eni_details': eni_details,
        'security_groups': security_groups
    }

def aws_network_graph(eni_details, security_groups):
    # Your existing code for the network graph

    # Create table for Security Groups and their rules
    sg_table_rows = []
    for sg in security_groups:
        sg_details = sg['details']
        sg_rules = sg['rules']
        sg_table_rows.append(html.Tr([
            html.Td(sg_details['GroupName']),
            html.Td(sg_details['GroupId']),
            html.Td(html.Ul([
                html.Li(f"{rule['IpProtocol']} {rule.get('FromPort', '')}-{rule.get('ToPort', '')} {rule['IpRanges']}")
                for rule in sg_rules
            ]))
        ]))

    sg_table = html.Table([
        html.Thead(html.Tr([
            html.Th("Group Name"),
            html.Th("Group ID"),
            html.Th("Rules")
        ])),
        html.Tbody(sg_table_rows)
    ])

    app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

    app.layout = dbc.Container([
        # Your existing layout
        dbc.Row([dbc.Col(sg_table, className="mt-4")])  # Add the security group table
    ])

    # Your existing callbacks

    app.run_server(debug=True)
￼Enter
