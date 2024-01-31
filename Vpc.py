import graphviz
import boto3
import argparse

def generate_aws_network_graph(account, region, ipv4, eni, subnet, route_table, destination_ipv4, tgw):
    # Connect to AWS using Boto3
    session = boto3.Session(
        aws_access_key_id='your_access_key',
        aws_secret_access_key='your_secret_key',
        region_name=region
    )

    ec2_client = session.client('ec2')

    # Fetch data from AWS based on user selections
    # Replace the placeholder logic with actual AWS API calls
    eni_options = [{'label': eni['NetworkInterfaceId'], 'value': eni['NetworkInterfaceId']} for eni in ec2_client.describe_network_interfaces()['NetworkInterfaces']]
    subnet_options = [{'label': subnet['SubnetId'], 'value': subnet['SubnetId']} for subnet in ec2_client.describe_subnets(Filters=[{'Name': 'vpc-id', 'Values': ['vpc-id']}])['Subnets']]
    route_table_options = [{'label': rt['RouteTableId'], 'value': rt['RouteTableId']} for rt in ec2_client.describe_route_tables(Filters=[{'Name': 'vpc-id', 'Values': ['vpc-id']}])['RouteTables']]
    tgw_options = [{'label': tgw['TransitGatewayId'], 'value': tgw['TransitGatewayId']} for tgw in ec2_client.describe_transit_gateways()['TransitGateways']]

    # Create a Graphviz graph
    dot = graphviz.Digraph(comment='AWS Networking Flow')

    # Example: Add nodes for ENI, Subnet, Route Table, Destination, TGW
    dot.node(eni, f'ENI {eni}')
    dot.node(subnet, f'Subnet {subnet}')
    dot.node(route_table, f'Route Table {route_table}')
    dot.node(destination_ipv4, f'Destination {destination_ipv4}')
    dot.node(tgw, f'Transit Gateway {tgw}')

    # Example: Add edges based on relationships
    dot.edge(eni, subnet)
    dot.edge(subnet, route_table)
    dot.edge(route_table, destination_ipv4)
    dot.edge(route_table, tgw)

    # Render and view the graph
    dot.render(filename='aws_network_flow', format='png', cleanup=True, view=True)

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

    generate_aws_network_graph(args.account, args.region, args.ipv4, args.eni, args.subnet, args.route_table, args.destination_ipv4, args.tgw)
￼Enter
