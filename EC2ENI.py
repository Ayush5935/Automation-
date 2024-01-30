import graphviz
import boto3

def generate_ec2_eni_graph(account_id, region):
    ec2_client = boto3.client('ec2', region_name=region)

    reservations = ec2_client.describe_instances().get('Reservations', [])

    nodes = set()
    edges = []

    for reservation in reservations:
        for instance in reservation.get('Instances', []):
            instance_id = instance.get('InstanceId')
            nodes.add(instance_id)

            for network_interface in instance.get('NetworkInterfaces', []):
                eni_id = network_interface.get('NetworkInterfaceId')
                nodes.add(eni_id)
                edges.append(f'{instance_id} -> {eni_id};')

    dot_code = generate_dot_code(nodes, edges)
    graph = graphviz.Source(dot_code)
    graph.render(filename="ec2_eni_graph", format="png", cleanup=True, view=True)

def generate_dot_code(nodes, edges):
    dot_code = "digraph EC2ENIGraph {\n"

    for node in nodes:
        dot_code += f'  "{node}";\n'

    for edge in edges:
        dot_code += f'  {edge}\n'

    dot_code += "}\n"
    return dot_code

# Example usage
generate_ec2_eni_graph("your_account_id", "your_region")
￼Enter
