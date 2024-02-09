import boto3
import csv

# Initialize Boto3 client for EC2
client = boto3.client('ec2')

# Function to retrieve mirror filters details
def get_mirror_filters():
    try:
        response = client.describe_traffic_mirror_filters()
        mirror_filters = response.get('TrafficMirrorFilters', [])
        return mirror_filters
    except Exception as e:
        print(f"Error retrieving mirror filters: {e}")
        return []

# Function to export data to CSV
def export_to_csv(data, filename):
    if not data:
        print(f"No data to export for {filename}")
        return
    try:
        with open(filename, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['FilterId', 'Description', 'RuleType', 'RuleId', 'RuleNumber', 'RuleAction'])  # Write header row
            for filter in data:
                filter_id = filter.get('TrafficMirrorFilterId', 'N/A')
                description = filter.get('Description', 'N/A')
                rules = filter.get('TrafficMirrorFilterRules', [])
                for rule in rules:
                    rule_id = rule.get('TrafficMirrorFilterRuleId', 'N/A')
                    rule_number = rule.get('RuleNumber', 'N/A')
                    rule_action = rule.get('RuleAction', 'N/A')
                    traffic_direction = rule.get('TrafficDirection', 'N/A')
                    if traffic_direction == 'ingress':
                        rule_type = 'IngressRule'
                    elif traffic_direction == 'egress':
                        rule_type = 'EgressRule'
                    else:
                        rule_type = 'Unknown'
                    writer.writerow([filter_id, description, rule_type, rule_id, rule_number, rule_action])
        print(f"Data exported to {filename} successfully.")
    except Exception as e:
        print(f"Error exporting data to {filename}: {e}")

# Main function
def main():
    # Get mirror filters details
    mirror_filters = get_mirror_filters()
    
    # Export mirror filter data to CSV
    export_to_csv(mirror_filters, 'mirror_filters.csv')

if __name__ == "__main__":
    main()
