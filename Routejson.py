import json
import argparse

def update_json(json_data, user_args):
    try:
        # Update JSON based on user arguments
        json_data[user_args['hosted_zone_name']] = {
            user_args['environment']: {
                user_args['region']: {
                    "value": user_args['hosted_zone_id']
                }
            }
        }

        return json_data
    except Exception as e:
        print(f"Error updating JSON: {e}")
        raise

if __name__ == '__main__':
    # Example JSON data
    example_json = {
        "nitin.test.com.": {
            'prod': {
                'us-east-1': {"value": "/hostedzone/Z08257087VWCD6793RCL"},
                'us-east-2': {"value": "/hostedzone/Z02558812KBN832VT9DRD"},
                'us-west-2': {"value": "/hostedzone/Z03945993IK07I25WAWJF"}
            }
        }
    }

    # Argument parser
    parser = argparse.ArgumentParser(description='Update JSON structure')
    parser.add_argument('--hosted_zone_name', required=True, help='Hosted Zone Name')
    parser.add_argument('--environment', required=True, help='Environment')
    parser.add_argument('--region', required=True, help='Region')
    parser.add_argument('--hosted_zone_id', required=True, help='Hosted Zone ID')
    args = parser.parse_args()

    # Update JSON based on user input
    updated_json = update_json(example_json, vars(args))

    # Print the updated JSON
    print(json.dumps(updated_json, indent=2))


python script_name.py --hosted_zone_name xyz.abc.com --environment Dev --region us-east-1 --hosted_zone_id Z08257087VWCD6793RCL
