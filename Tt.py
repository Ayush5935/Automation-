import boto3
import csv

# Initialize Boto3 client for EC2
client = boto3.client('ec2')

# Function to retrieve mirror filters details
def get_mirror_filters():
    try:
        response = client.describe_traffic_mirror_filters()
        mirror_filters = response.get('TrafficMirrorFilters', [])
        formatted_filters = []
        for mirror_filter in mirror_filters:
            ingress_rules = format_filter_rules(mirror_filter.get('IngressFilterRules', []))
            egress_rules = format_filter_rules(mirror_filter.get('EgressFilterRules', []))
            formatted_filter = {
                'FilterId': mirror_filter.get('TrafficMirrorFilterId', ''),
                'Description': mirror_filter.get('Description', ''),
                'IngressFilterRules': '\n'.join(ingress_rules),
                'EgressFilterRules': '\n'.join(egress_rules)
            }
            formatted_filters.append(formatted_filter)
        return formatted_filters
    except Exception as e:
        print(f"Error retrieving mirror filters: {e}")
        return []

# Function to format filter rules
def format_filter_rules(rules):
    formatted_rules = []
    for rule in rules:
        formatted_rule = {
            'RuleId': rule.get('TrafficMirrorFilterRuleId', ''),
            'TrafficDirection': rule.get('TrafficDirection', ''),
            'RuleAction': rule.get('RuleAction', ''),
            'RuleNumber': rule.get('RuleNumber', '')
            # Add more details if needed
        }
        formatted_rules.append(formatted_rule)
    return formatted_rules

# Function to export data to CSV
def export_to_csv(data, filename):
    if not data:
        print(f"No data to export for {filename}")
        return
    try:
        with open(filename, 'w', newline='') as csvfile:
            fieldnames = ['FilterId', 'Description', 'IngressFilterRules', 'EgressFilterRules']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for item in data:
                writer.writerow(item)
        print(f"Data exported to {filename} successfully.")
    except Exception as e:
        print(f"Error exporting data to {filename}: {e}")

# Main function
def main():
    # Get mirror filters details
    mirror_filters = get_mirror_filters()
    export_to_csv(mirror_filters, 'mirror_filters.csv')

if __name__ == "__main__":
    main()
