import json

SOURCE_ACCOUNT_ID = '123456789012'  # Replace with your source account ID
DESTINATION_ACCOUNT_ID = '987654321098'  # Replace with your destination account ID
AWS_REGION = 'us-east-2'

def create_kms_key_demo():
    # This is a demo function that simulates creating a KMS key
    # In a real scenario, you would use the AWS CLI or SDK to create a KMS key
    demo_key_id = 'arn:aws:kms:' + AWS_REGION + ':123456789012:key/demo-key-id'
    return demo_key_id

def set_kms_policy_demo(key_id):
    try:
        kms_policy = {
            "Version": "2012-10-17",
            "Id": "kms-policy-for-ami-copy",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {"AWS": f"arn:aws:iam::{SOURCE_ACCOUNT_ID}:root"},
                    "Action": ["kms:Encrypt", "kms:GenerateDataKey", "kms:Decrypt"],
                    "Resource": f"{key_id}"
                },
                {
                    "Effect": "Allow",
                    "Principal": {"AWS": f"arn:aws:iam::{DESTINATION_ACCOUNT_ID}:root"},
                    "Action": ["kms:Decrypt", "kms:GenerateDataKey"],
                    "Resource": f"{key_id}"
                }
            ]
        }

        policy_json = json.dumps(kms_policy, indent=2)
        print("KMS Policy set:")
        print(policy_json)

        # Save policy to a JSON file
        with open('kms_policy.json', 'w') as file:
            file.write(policy_json)

        print("Policy saved to 'kms_policy.json'")
        return policy_json
    except Exception as e:
        print(f"Error setting KMS policy: {e}")
        raise

if __name__ == '__main__':
    try:
        # Create a demo KMS key
        kms_key_id_demo = create_kms_key_demo()
        print(f"Demo KMS Key created with ID: {kms_key_id_demo}")

        # Set the demo KMS policy
        policy_json_demo = set_kms_policy_demo(kms_key_id_demo)
    except Exception as e:
        print(f"An error occurred: {e}")



expected output 

Demo KMS Key created with ID: arn:aws:kms:us-east-2:123456789012:key/demo-key-id
KMS Policy set:
{
  "Version": "2012-10-17",
  "Id": "kms-policy-for-ami-copy",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::123456789012:root"
      },
      "Action": [
        "kms:Encrypt",
        "kms:GenerateDataKey",
        "kms:Decrypt"
      ],
      "Resource": "arn:aws:kms:us-east-2:123456789012:key/demo-key-id"
    },
    {
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::987654321098:root"
      },
      "Action": [
        "kms:Decrypt",
        "kms:GenerateDataKey"
      ],
      "Resource": "arn:aws:kms:us-east-2:123456789012:key/demo-key-id"
    }
  ]
}
Policy saved to 'kms_policy.json'



import argparse
import json
import boto3

def create_kms_key_demo():
    # Replace this with your actual code to create a KMS key
    # ...

def set_kms_policy_demo(key_id):
    # Replace this with your actual code to set KMS policy
    # ...

def copy_ami(source_account, source_region, source_ami, target_account, target_region):
    # Replace this with your actual code to copy AMI
    # ...

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Copy AMI and create KMS Key Policy')
    parser.add_argument('--source', required=True, help='Source AWS account ID')
    parser.add_argument('--source_region', required=True, help='Source AWS region')
    parser.add_argument('--ami', required=True, help='Source AMI ID to be copied')
    parser.add_argument('--target', required=True, help='Destination AWS account ID')
    parser.add_argument('--target_region', required=True, help='Destination AWS region')
    
    args = parser.parse_args()

    # Copy AMI
    ami_copy_result = copy_ami(args.source, args.source_region, args.ami, args.target, args.target_region)
    
    # Create KMS Key and Policy
    kms_key_id_demo = create_kms_key_demo()
    policy_json_demo = set_kms_policy_demo(kms_key_id_demo)

    # Print terminal output
    print(f"AMI {args.ami} got copied from source account {args.source} in region {args.source_region} to "
          f"destination account {args.target} in region {args.target_region}")

    # Save the result to JSON file
    output_data = {
        "Copied_AMI_ID": ami_copy_result,  # Replace ami_copy_result with actual result
        "KMS_Policy_JSON": json.loads(policy_json_demo)
    }
    with open('output.json', 'w') as json_file:
        json.dump(output_data, json_file, indent=2)
