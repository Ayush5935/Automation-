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
            writer.writerow(['FilterId', 'Description', 'Rule', 'TrafficDirection'])  # Write header row
            for item in data:
                filter_id = item.get('FilterId', 'N/A')
                description = item.get('Description', 'N/A')
                rules = item.get('Rules', [])
                for rule in rules:
                    rule_id = rule.get('RuleId', 'N/A')
                    rule_number = rule.get('RuleNumber', 'N/A')
                    rule_action = rule.get('RuleAction', 'N/A')
                    rule_details = f"RuleID: {rule_id}\nRuleNumber: {rule_number}\nRuleAction: {rule_action}"
                    writer.writerow([filter_id, description, rule_details, rule.get('TrafficDirection', 'N/A')])
        print(f"Data exported to {filename} successfully.")
    except Exception as e:
        print(f"Error exporting data to {filename}: {e}")

# Main function
def main():
    # Get mirror filters details
    mirror_filters = get_mirror_filters()
    
    # Prepare data for CSV export
    export_data = []
    for filter in mirror_filters:
        filter_id = filter.get('TrafficMirrorFilterId', 'N/A')
        description = filter.get('Description', 'N/A')
        rules = filter.get('TrafficMirrorFilterRules', [])
        export_data.append({'FilterId': filter_id, 'Description': description, 'Rules': rules})
    
    # Export mirror filter data to CSV
    export_to_csv(export_data, 'mirror_filters.csv')

if __name__ == "__main__":
    main()
￼Enter
