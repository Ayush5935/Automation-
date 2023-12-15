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
