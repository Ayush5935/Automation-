import dash
from dash import html, dcc
from dash.dependencies import Input, Output
from dash_cytoscape import Cytoscape
import boto3

app = dash.Dash(__name__)

# Define layout
app.layout = html.Div([
    html.Label('Select Source Account'),
    dcc.Dropdown(
        id='account-dropdown',
        options=[
            {'label': 'Account 1', 'value': 'account1'},
            {'label': 'Account 2', 'value': 'account2'},
            # Add more accounts as needed
        ],
        value='account1'
    ),

    html.Label('Select Source Region'),
    dcc.Dropdown(
        id='region-dropdown',
        options=[
            {'label': 'Region 1', 'value': 'region1'},
            {'label': 'Region 2', 'value': 'region2'},
            # Add more regions as needed
        ],
        value='region1'
    ),

import dash
from dash import html, dcc
from dash.dependencies import Input, Output
from dash_cytoscape import Cytoscape
import boto3

app = dash.Dash(__name__)

# Define layout
app.layout = html.Div([
    html.Label('Select Source Account'),
    dcc.Dropdown(
        id='account-dropdown',
        options=[
            {'label': 'Account 1', 'value': 'account1'},
            {'label': 'Account 2', 'value': 'account2'},
            # Add more accounts as needed
        ],
        value='account1'
    ),

    html.Label('Select Source Region'),
    dcc.Dropdown(
        id='region-dropdown',
        options=[
            {'label': 'Region 1', 'value': 'region1'},
            {'label': 'Region 2', 'value': 'region2'},
            # Add more regions as needed
        ],
        value='region1'
    ),

    html.Label('Select a Source Private IPv4'),
    dcc.Input(id='ipv4-input', type='text', value=''),

    html.Label('Select a Source ENI'),
    dcc.Dropdown(id='eni-dropdown'),

    html.Label('Select a Source Subnet ID'),
    dcc.Dropdown(id='subnet-dropdown'),

    html.Label('Select a Source Route Table ID'),
    dcc.Dropdown(id='route-table-dropdown'),

    html.Label('Select a Destination Private IPv4'),
    dcc.Input(id='destination-ipv4-input', type='text', value=''),

    html.Label('Select a Source TGW'),
    dcc.Dropdown(id='tgw-dropdown'),

    Cytoscape(
        id='graph',
        layout={'name': 'circle'},
        style={'width': '100%', 'height': '600px'},
        elements=[]  # Elements will be updated dynamically
    )
])

# Define callback to update dropdown options based on user selections
@app.callback(
    [Output('eni-dropdown', 'options'),
     Output('subnet-dropdown', 'options'),
     Output('route-table-dropdown', 'options'),
     Output('tgw-dropdown', 'options')],
    [Input('account-dropdown', 'value'),
     Input('region-dropdown', 'value')]
)
def update_dropdowns(selected_account, selected_region):
    # Connect to AWS using Boto3
    session = boto3.Session(
        aws_access_key_id='your_access_key',
        aws_secret_access_key='your_secret_key',
        region_name=selected_region
    )

    ec2_client = session.client('ec2')

    # Fetch data from AWS based on user selections
    # Replace the placeholder logic with actual AWS API calls
    eni_options = [{'label': eni['NetworkInterfaceId'], 'value': eni['NetworkInterfaceId']} for eni in ec2_client.describe_network_interfaces()['NetworkInterfaces']]
    subnet_options = [{'label': subnet['SubnetId'], 'value': subnet['SubnetId']} for subnet in ec2_client.describe_subnets(Filters=[{'Name': 'vpc-id', 'Values': ['vpc-id']}])['Subnets']]
    route_table_options = [{'label': rt['RouteTableId'], 'value': rt['RouteTableId']} for rt in ec2_client.describe_route_tables(Filters=[{'Name': 'vpc-id', 'Values': ['vpc-id']}])['RouteTables']]
    tgw_options = [{'label': tgw['TransitGatewayId'], 'value': tgw['TransitGatewayId']} for tgw in ec2_client.describe_transit_gateways()['TransitGateways']]

    return eni_options, subnet_options, route_table_options, tgw_options

# Define callback to update graph based on user selections
@app.callback(
    Output('graph', 'elements'),
    [Input('account-dropdown', 'value'),
     Input('region-dropdown', 'value'),
     Input('ipv4-input', 'value'),
     Input('eni-dropdown', 'value'),
     Input('subnet-dropdown', 'value'),
     Input('route-table-dropdown', 'value'),
     Input('destination-ipv4-input', 'value'),
     Input('tgw-dropdown', 'value')]
)
def update_graph(selected_account, selected_region, source_ipv4, source_eni, source_subnet, source_route_table, destination_ipv4, source_tgw):
    # Fetch data from AWS and build the graph based on user selections
    # Replace the placeholder logic with actual AWS API calls and graph-building logic
    elements = []

    # Build the graph based on fetched data

    return elements

if __name__ == '__main__':
    app.run_server(debug=True)
￼Enter
