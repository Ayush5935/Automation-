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
            for ingress_rule in ingress_rules:
                formatted_filter = {
                    'FilterId': mirror_filter.get('TrafficMirrorFilterId', ''),
                    'Description': mirror_filter.get('Description', ''),
                    'RuleType': 'Ingress',
                    'RuleDetails': ingress_rule
                }
                formatted_filters.append(formatted_filter)
            for egress_rule in egress_rules:
                formatted_filter = {
                    'FilterId': mirror_filter.get('TrafficMirrorFilterId', ''),
                    'Description': mirror_filter.get('Description', ''),
                    'RuleType': 'Egress',
                    'RuleDetails': egress_rule
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
        formatted_rule = (
            f"RuleId: {rule.get('TrafficMirrorFilterRuleId', '')}, "
            f"RuleAction: {rule.get('RuleAction', '')}, "
            f"RuleNumber: {rule.get('RuleNumber', '')}"
            # Add more details if needed
        )
        formatted_rules.append(formatted_rule)
    return formatted_rules

# Function to export data to CSV for mirror filters
def export_mirror_filters_to_csv(data, filename):
    if not data:
        print(f"No data to export for {filename}")
        return
    try:
        with open(filename, 'w', newline='') as csvfile:
            fieldnames = ['FilterId', 'Description', 'RuleType', 'RuleDetails']
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
    export_mirror_filters_to_csv(mirror_filters, 'mirror_filters.csv')

if __name__ == "__main__":
    main()
￼Enter
