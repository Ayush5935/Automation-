import boto3
import json

AWS_REGION = 'us-east-2'
SOURCE_ACCOUNT_ID = 'source_account_id'
DESTINATION_ACCOUNT_ID = 'destination_account_id'
REGION = 'us-east-2'

kms_client = boto3.client('kms', region_name=AWS_REGION)

def create_kms_key():
    try:
        response = kms_client.create_key()
        key_id = response['KeyMetadata']['KeyId']
        return key_id
    except Exception as e:
        print(f"Error creating KMS key: {e}")
        raise

def set_kms_policy(key_id):
    try:
        kms_policy = {
            "Version": "2012-10-17",
            "Id": "kms-policy-for-ami-copy",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {"AWS": f"arn:aws:iam::{SOURCE_ACCOUNT_ID}:root"},
                    "Action": ["kms:Encrypt", "kms:GenerateDataKey", "kms:Decrypt"],
                    "Resource": f"arn:aws:kms:{REGION}:{key_id}"
                },
                {
                    "Effect": "Allow",
                    "Principal": {"AWS": f"arn:aws:iam::{DESTINATION_ACCOUNT_ID}:root"},
                    "Action": ["kms:Decrypt", "kms:GenerateDataKey"],
                    "Resource": f"arn:aws:kms:{REGION}:{key_id}"
                }
            ]
        }

        policy_json = json.dumps(kms_policy, indent=2)
        kms_client.put_key_policy(
            KeyId=key_id,
            PolicyName='default',
            Policy=policy_json
        )
        return policy_json
    except Exception as e:
        print(f"Error setting KMS policy: {e}")
        raise

if __name__ == '__main__':
    try:
        # Create a KMS key
        kms_key_id = create_kms_key()
        print(f"KMS Key created with ID: {kms_key_id}")

        # Set the KMS policy
        policy_json = set_kms_policy(kms_key_id)
        print("KMS Policy set:")
        print(policy_json)
    except Exception as e:
        print(f"An error occurred: {e}")




# expected output 

KMS Key created with ID: arn:aws:kms:us-east-2:123456789012:key/abcd1234-a123-456a-a12b-a123b4cd5678
KMS Policy set:
{
  "Version": "2012-10-17",
  "Id": "kms-policy-for-ami-copy",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::source_account_id:root"
      },
      "Action": [
        "kms:Encrypt",
        "kms:GenerateDataKey",
        "kms:Decrypt"
      ],
      "Resource": "arn:aws:kms:us-east-2:abcd1234-a123-456a-a12b-a123b4cd5678"
    },
    {
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::destination_account_id:root"
      },
      "Action": [
        "kms:Decrypt",
        "kms:GenerateDataKey"
      ],
      "Resource": "arn:aws:kms:us-east-2:abcd1234-a123-456a-a12b-a123b4cd5678"
    }
  ]
}


