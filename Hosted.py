import csv
import json

def csv_to_json(csv_file_path):
    json_data = {}

    with open(csv_file_path, newline='') as csvfile:
        csv_reader = csv.DictReader(csvfile)
        
        for row in csv_reader:
            hosted_zone_name = row['Hosted Zone Name'].lower()  # Convert to lowercase
            record_type = row['Type'].lower()  # Convert to lowercase
            created_by = row['Created By']
            record_count = row['Record Count']
            hosted_zone_id = row['Hosted Zone ID']
            environment = row['Environment'].lower()  # Convert to lowercase
            region = row['Region'].lower()  # Convert to lowercase

            if hosted_zone_name not in json_data:
                json_data[hosted_zone_name] = {}

            if environment not in json_data[hosted_zone_name]:
                json_data[hosted_zone_name][environment] = {}

            if region:
                json_data[hosted_zone_name][environment][region] = {
                    "value": f"/hostedzone/{hosted_zone_id}"
                }
            else:
                json_data[hosted_zone_name][environment] = {
                    "value": f"/hostedzone/{hosted_zone_id}"
                }

    return json_data

def save_json(json_data, json_file_path):
    with open(json_file_path, 'w') as jsonfile:
        json.dump(json_data, jsonfile, indent=2)

# Example usage
csv_file_path = 'your_csv_file.csv'
json_data = csv_to_json(csv_file_path)
save_json(json_data, 'output.json')
