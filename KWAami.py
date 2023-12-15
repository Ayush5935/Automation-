import json
import argparse
import boto3

def create_kms_key():
    try:
        kms_client = boto3.client('kms', region_name=args.source_region)
        response = kms_client.create_key()
        key_id = response['KeyMetadata']['KeyId']
        print(f"KMS Key created with ID: {key_id}")
        return key_id
    except Exception as e:
        print(f"Error creating KMS key: {e}")
        raise

def set_kms_policy(key_id):
    try:
        kms_policy = {
            "Id": "key-consolepolicy-3",
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "Enable IAM User Permissions",
                    "Effect": "Allow",
                    "Principal": {"AWS": f"arn:aws:iam::{args.source}:root"},
                    "Action": "kms:*",
                    "Resource": "*"
                },
                {
                    "Sid": "Allow use of the key",
                    "Effect": "Allow",
                    "Principal": {"AWS": f"arn:aws:iam::{args.target}:root"},
                    "Action": [
                        "kms:Encrypt",
                        "kms:Decrypt",
                        "kms:ReEncrypt*",
                        "kms:GenerateDataKey*",
                        "kms:DescribeKey"
                    ],
                    "Resource": "*"
                },
                {
                    "Sid": "Allow attachment of persistent resources",
                    "Effect": "Allow",
                    "Principal": {"AWS": f"arn:aws:iam::{args.target}:root"},
                    "Action": [
                        "kms:CreateGrant",
                        "kms:ListGrants",
                        "kms:RevokeGrant"
                    ],
                    "Resource": "*",
                    "Condition": {
                        "Bool": {"kms:GrantIsForAWSResource": "true"}
                    }
                }
            ]
        }

        policy_json = json.dumps(kms_policy, indent=2)
        print("KMS Policy set:")
        print(policy_json)

        kms_client = boto3.client('kms', region_name=args.source_region)
        kms_client.put_key_policy(
            KeyId=key_id,
            PolicyName='default',
            Policy=policy_json
        )

        print(f"Policy attached to KMS Key {key_id}")
        return key_id
    except Exception as e:
        print(f"Error setting KMS policy: {e}")
        raise

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Create KMS Key and attach KMS Key Policy')
    parser.add_argument('--source', required=True, help='Source AWS account ID')
    parser.add_argument('--source_region', required=True, help='Source AWS region')
    parser.add_argument('--target', required=True, help='Destination AWS account ID')
    parser.add_argument('--target_region', required=True, help='Destination AWS region')
    args = parser.parse_args()

    # Create a KMS key
    kms_key_id = create_kms_key()

    # Set the KMS policy
    policy_json_demo = set_kms_policy(kms_key_id)

    print(f"KMS Key {kms_key_id} created and policy attached.")




## with Alias name

import json
import argparse
import boto3

def create_kms_key(alias_name):
    try:
        kms_client = boto3.client('kms', region_name=args.source_region)
        response = kms_client.create_key()
        key_id = response['KeyMetadata']['KeyId']

        # Set alias for the KMS key
        kms_client.create_alias(
            AliasName=f'alias/{alias_name}',
            TargetKeyId=key_id
        )

        print(f"KMS Key created with ID: {key_id} and alias: {alias_name}")
        return key_id
    except Exception as e:
        print(f"Error creating KMS key: {e}")
        raise

def set_kms_policy(key_id):
    try:
        kms_policy = {
            "Id": "key-consolepolicy-3",
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "Enable IAM User Permissions",
                    "Effect": "Allow",
                    "Principal": {"AWS": f"arn:aws:iam::{args.source}:root"},
                    "Action": "kms:*",
                    "Resource": "*"
                },
                {
                    "Sid": "Allow use of the key",
                    "Effect": "Allow",
                    "Principal": {"AWS": f"arn:aws:iam::{args.target}:root"},
                    "Action": [
                        "kms:Encrypt",
                        "kms:Decrypt",
                        "kms:ReEncrypt*",
                        "kms:GenerateDataKey*",
                        "kms:DescribeKey"
                    ],
                    "Resource": "*"
                },
                {
                    "Sid": "Allow attachment of persistent resources",
                    "Effect": "Allow",
                    "Principal": {"AWS": f"arn:aws:iam::{args.target}:root"},
                    "Action": [
                        "kms:CreateGrant",
                        "kms:ListGrants",
                        "kms:RevokeGrant"
                    ],
                    "Resource": "*",
                    "Condition": {
                        "Bool": {"kms:GrantIsForAWSResource": "true"}
                    }
                }
            ]
        }

        policy_json = json.dumps(kms_policy, indent=2)
        print("KMS Policy set:")
        print(policy_json)

        kms_client = boto3.client('kms', region_name=args.source_region)
        kms_client.put_key_policy(
            KeyId=key_id,
            PolicyName='default',
            Policy=policy_json
        )

        print(f"Policy attached to KMS Key {key_id}")
        return key_id
    except Exception as e:
        print(f"Error setting KMS policy: {e}")
        raise

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Create KMS Key and attach KMS Key Policy')
    parser.add_argument('--source', required=True, help='Source AWS account ID')
    parser.add_argument('--source_region', required=True, help='Source AWS region')
    parser.add_argument('--target', required=True, help='Destination AWS account ID')
    parser.add_argument('--target_region', required=True, help='Destination AWS region')
    parser.add_argument('--alias', required=True, help='Alias for the KMS key')
    args = parser.parse_args()

    # Create a KMS key with alias
    kms_key_id = create_kms_key(args.alias)

    # Set the KMS policy
    policy_json_demo = set_kms_policy(kms_key_id)

    print(f"KMS Key {kms_key_id} created with alias '{args.alias}' and policy attached.")

