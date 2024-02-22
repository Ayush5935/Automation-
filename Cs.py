import boto3
import csv

# Regions to search
regions = ["us-west-1", "us-west-2", "us-east-1", "us-east-2"]

# Function to get instances matching the specified naming pattern
def get_instances(region):
    ec2_client = boto3.client("ec2", region_name=region)
    response = ec2_client.describe_instances(
        Filters=[
            {"Name": "tag:Name", "Values": ["CS-PE*", "CS-R*"]}
        ]
    )
    instances = response["Reservations"]
    return instances

# Function to extract required information
def extract_info(instances):
    instance_data = []
    for reservation in instances:
        for instance in reservation["Instances"]:
            instance_id = instance["InstanceId"]
            subnet_id = instance["SubnetId"]
            private_ip = instance["PrivateIpAddress"]
            vpc_id = instance["VpcId"]
            vpc_name = get_vpc_name(vpc_id)
            instance_data.append([instance_id, subnet_id, private_ip, vpc_name, vpc_id])
    return instance_data

# Function to get VPC name
def get_vpc_name(vpc_id):
    ec2 = boto3.resource("ec2")
    vpc = ec2.Vpc(vpc_id)
    for tag in vpc.tags or []:
        if tag["Key"] == "Name":
            return tag["Value"]
    return ""

# Function to save data to CSV
def save_to_csv(data):
    with open("aws_instances.csv", "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Instance ID", "Subnet ID", "Private IP", "VPC Name", "VPC ID"])
        writer.writerows(data)

# Main function
def main():
    all_instance_data = []
    for region in regions:
        instances = get_instances(region)
        instance_data = extract_info(instances)
        all_instance_data.extend(instance_data)
    save_to_csv(all_instance_data)

if __name__ == "__main__":
    main()
￼Enter
