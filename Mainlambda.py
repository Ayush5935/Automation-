import json
import boto3
import os
import uuid
import session

db = database.DatabaseWrapper()

def worker_nodes(eks, region):
    client = boto3.client('ec2', region_name=region)
    tag_key = 'kubernetes.io/cluster/' + eks
    tag_value = 'owned'
    response = client.describe_instances(
        Filters=[
            {'Name': 'tag-key', 'Values': [tag_key]}
        ]
    )

    instance_count = 0

    for reservation in response['Reservations']:
        for instance in reservation['Instances']:
            instance_count += 1

    return instance_count

def insert_and_update(item):
    data = db.query_data_on_the_basis_of_cluster(item["eksClusterName"], item['account'], item['awsRegion'])

    if len(data["Items"]) == 0:
        item['id'] = str(uuid.uuid1())
        response = db.add(item)
        return item['id']

    for oitem in data["Items"]:
        pdhv = ''
        pdv = ''

        if 'prismaDefenderVersion' in oitem:
            pdv = oitem['prismaDefenderVersion']
        if 'prismaDefenderHelmVersion' in oitem:
            pdhv = oitem['prismaDefenderHelmVersion']

        if oitem['clusterError'] != item['clusterError']:
            db.update_data(oitem['id'], item["eksClusterName"], pdv, pdhv, item['clusterError'], item['isv'],
                            item['environment'])
        else:
            db.update_data(oitem['id'], item["eksClusterName"], pdv, pdhv, item['clusterError'], item['isv'],
                            item['environment'])

        return oitem['id']

def find_regions():
    credentials = session.assumerole(os.environ.get('ECR_IAM_ROLE_ARN'))
    client = boto3.client(
        'ssm',
        region_name='us-west-2',
        aws_access_key_id=credentials['AccessKeyId'],
        aws_secret_access_key=credentials['SecretAccessKey'],
        aws_session_token=credentials['SessionToken']
    )

    response = client.get_parameter(Name="/prisma/twistlock/defender/regions")
    regions = response['Parameter']['Value'].split(",")
    return regions

def find_latest_image():
    credentials = session.assumerole(os.environ.get('ECR_IAM_ROLE_ARN'))
    client = boto3.client(
        'ecr',
        region_name='us-west-2',
        aws_access_key_id=credentials['AccessKeyId'],
        aws_secret_access_key=credentials['SecretAccessKey'],
        aws_session_token=credentials['SessionToken']
    )

    response = client.describe_images(repositoryName='cicd/charts/twistlock')
    latestImage = ''
    images = response['imageDetails']

    sorted_images = sorted(images, key=lambda x: x['imagePushedAt'], reverse=True)

    for image in sorted_images:
        latestImage = image['imageTags'][0]
        break

    return latestImage

def delete_unwanted_entries(clusters, account, region):
    data = db.query_data_on_the_basis_of_account(account)

    for item in data["Items"]:
        if item['awsRegion'] == region:
            if item['eksClusterName'] in clusters['clusters']:
                print("DO NOT DELETE")
            else:
                print("DELETE")
                db.delete(item['id'], item['eksClusterName'])

def lambda_handler(event, context):
    if 'action' in event and event['action'] == 'scanner':
        final = []
        print(context.invoked_function_arn)
        account = context.invoked_function_arn.split(":")[4]
        regions = find_regions()

        for region in regions:
            sess = boto3.Session(region_name=region)

            try:
                eks = sess.client('eks')
                cfn = sess.client('cloudformation')
                clusters = eks.list_clusters()
                delete_unwanted_entries(clusters, account, region)

                for cluster in clusters["clusters"]:
                    result = eks.describe_cluster(name=cluster)
                    isv = ""
                    version = result["cluster"]["version"]

                    if "dish:deployment:isv-name" not in result["cluster"]["tags"]:
                        isv = cluster.split("-")[0]
                    else:
                        isv = result["cluster"]["tags"]["dish:deployment:isv-name"]

                    environment = ""

                    if "dish:deployment:environment" not in result["cluster"]["tags"]:
                        if "dev" in cluster or "int" in cluster:
                            environment = "dev"
                        else:
                            environment = "prod"
                    else:
                        environment = result["cluster"]["tags"]["dish:deployment:environment"]

                    if "tags" not in result["cluster"]:
                        insert_and_update({
                            "eksClusterName": cluster,
                            "account": account,
                            "awsRegion": region,
                            "clusterError": "tags not present",
                            "isv": isv,
                            "environment": environment,
                            "version": version
                        })
                        continue

                    if "dish:deployment:stack-name" not in result["cluster"]["tags"]:
                        insert_and_update({
                            "eksClusterName": cluster,
                            "account": account,
                            "awsRegion": region,
                            "clusterError": "cloudformation tags not present",
                            "isv": isv,
                            "environment": environment,
                            "version": version
                        })
                        continue

                    stacks = cfn.describe_stacks(StackName=result["cluster"]["tags"]['dish:deployment:stack-name'])

                    if len(stacks['Stacks']) == 0:
                        insert_and_update({
                            "eksClusterName": cluster,
                            "account": account,
                            "awsRegion": region,
                            "clusterError": "No Stack Found",
                            "isv": isv,
                            "environment": environment,
                            "version": version
                        })
                        continue

                    if "Outputs" not in stacks['Stacks'][0]:
                        insert_and_update({
                            "eksClusterName": cluster,
                            "account": account,
                            "awsRegion": region,
                            "clusterError": "No Output parameters of Stack",
                            "isv": isv,
                            "environment": environment,
                            "version": version
                        })
                        continue

                    flag = False

                    for output in stacks["Stacks"][0]["Outputs"]:
                        if output["OutputKey"] == "EKSClusteraddClusterConfigCommand8D1DE1D0":
                            flag = True
                            id = insert_and_update({
                                "eksClusterName": cluster,
                                "account": account,
                                "awsRegion": region,
                                "clusterError": "",
                                "eksKubeconfig": output["OutputValue"],
                                "isv": isv,
                                "environment": environment,
                                "worker_nodes": worker_nodes(cluster, region),
                                "version": version
                            })
                            print(id)
                            final.append({
                                "EKS_CLUSTER_NAME": cluster,
import json
import boto3
import os
import uuid
import session

db = database.DatabaseWrapper()

def worker_nodes(eks, region):
    client = boto3.client('ec2', region_name=region)
    tag_key = 'kubernetes.io/cluster/' + eks
    tag_value = 'owned'
    response = client.describe_instances(
        Filters=[
            {'Name': 'tag-key', 'Values': [tag_key]}
        ]
    )

    instance_count = 0

    for reservation in response['Reservations']:
        for instance in reservation['Instances']:
            instance_count += 1

    return instance_count

def insert_and_update(item):
    data = db.query_data_on_the_basis_of_cluster(item["eksClusterName"], item['account'], item['awsRegion'])

    if len(data["Items"]) == 0:
        item['id'] = str(uuid.uuid1())
        response = db.add(item)
        return item['id']

    for oitem in data["Items"]:
        pdhv = ''
        pdv = ''

        if 'prismaDefenderVersion' in oitem:
            pdv = oitem['prismaDefenderVersion']
        if 'prismaDefenderHelmVersion' in oitem:
            pdhv = oitem['prismaDefenderHelmVersion']

        if oitem['clusterError'] != item['clusterError']:
            db.update_data(oitem['id'], item["eksClusterName"], pdv, pdhv, item['clusterError'], item['isv'],
                            item['environment'])
        else:
            db.update_data(oitem['id'], item["eksClusterName"], pdv, pdhv, item['clusterError'], item['isv'],
                            item['environment'])

        return oitem['id']

def find_regions():
    credentials = session.assumerole(os.environ.get('ECR_IAM_ROLE_ARN'))
    client = boto3.client(
        'ssm',
        region_name='us-west-2',
        aws_access_key_id=credentials['AccessKeyId'],
        aws_secret_access_key=credentials['SecretAccessKey'],
        aws_session_token=credentials['SessionToken']
    )

    response = client.get_parameter(Name="/prisma/twistlock/defender/regions")
    regions = response['Parameter']['Value'].split(",")
    return regions

def find_latest_image():
    credentials = session.assumerole(os.environ.get('ECR_IAM_ROLE_ARN'))
    client = boto3.client(
        'ecr',
        region_name='us-west-2',
        aws_access_key_id=credentials['AccessKeyId'],
        aws_secret_access_key=credentials['SecretAccessKey'],
        aws_session_token=credentials['SessionToken']
    )

    response = client.describe_images(repositoryName='cicd/charts/twistlock')
    latestImage = ''
    images = response['imageDetails']

    sorted_images = sorted(images, key=lambda x: x['imagePushedAt'], reverse=True)

    for image in sorted_images:
        latestImage = image['imageTags'][0]
        break

    return latestImage

def delete_unwanted_entries(clusters, account, region):
    data = db.query_data_on_the_basis_of_account(account)

    for item in data["Items"]:
        if item['awsRegion'] == region:
            if item['eksClusterName'] in clusters['clusters']:
                print("DO NOT DELETE")
            else:
                print("DELETE")
                db.delete(item['id'], item['eksClusterName'])

def lambda_handler(event, context):
    if 'action' in event and event['action'] == 'scanner':
        final = []
        print(context.invoked_function_arn)
        account = context.invoked_function_arn.split(":")[4]
        regions = find_regions()

        for region in regions:
            sess = boto3.Session(region_name=region)

            try:
                eks = sess.client('eks')
                cfn = sess.client('cloudformation')
                clusters = eks.list_clusters()
                delete_unwanted_entries(clusters, account, region)

                for cluster in clusters["clusters"]:
                    result = eks.describe_cluster(name=cluster)
                    isv = ""
                    version = result["cluster"]["version"]

                    if "dish:deployment:isv-name" not in result["cluster"]["tags"]:
                        isv = cluster.split("-")[0]
                    else:
                        isv = result["cluster"]["tags"]["dish:deployment:isv-name"]

                    environment = ""

                    if "dish:deployment:environment" not in result["cluster"]["tags"]:
                        if "dev" in cluster or "int" in cluster:
                            environment = "dev"
                        else:
                            environment = "prod"
                    else:
                        environment = result["cluster"]["tags"]["dish:deployment:environment"]

                    if "tags" not in result["cluster"]:
                        insert_and_update({
                            "eksClusterName": cluster,
                            "account": account,
                            "awsRegion": region,
                            "clusterError": "tags not present",
                            "isv": isv,
                            "environment": environment,
                            "version": version
                        })
                        continue

                    if "dish:deployment:stack-name" not in result["cluster"]["tags"]:
                        insert_and_update({
                            "eksClusterName": cluster,
                            "account": account,
                            "awsRegion": region,
                            "clusterError": "cloudformation tags not present",
                            "isv": isv,
                            "environment": environment,
                            "version": version
                        })
                        continue

                    stacks = cfn.describe_stacks(StackName=result["cluster"]["tags"]['dish:deployment:stack-name'])

                    if len(stacks['Stacks']) == 0:
                        insert_and_update({
                            "eksClusterName": cluster,
                            "account": account,
                            "awsRegion": region,
                            "clusterError": "No Stack Found",
                            "isv": isv,
                            "environment": environment,
                            "version": version
                        })
                        continue

                    if "Outputs" not in stacks['Stacks'][0]:
                        insert_and_update({
                            "eksClusterName": cluster,
                            "account": account,
                            "awsRegion": region,
                            "clusterError": "No Output parameters of Stack",
                            "isv": isv,
                            "environment": environment,
                            "version": version
                        })
                        continue

                    flag = False

                    for output in stacks["Stacks"][0]["Outputs"]:
                        if output["OutputKey"] == "EKSClusteraddClusterConfigCommand8D1DE1D0":
                            flag = True
                            id = insert_and_update({
                                "eksClusterName": cluster,
                                "account": account,
                                "awsRegion": region,
                                "clusterError": "",
                                "eksKubeconfig": output["OutputValue"],
                                "isv": isv,
                                "environment": environment,
                                "worker_nodes": worker_nodes(cluster, region),
                                "version": version
                            })
                            print(id)
                            final.append({
                                "EKS_CLUSTER_NAME": cluster,
                                "REGION": region,
                                "ACCOUNT": account,
                                "DYNAMODB_IAM_ROLE_ARN": os.environ.get('DYNAMODB_IAM_ROLE_ARN'),
                                "DYNAMODB_TABLE_NAME": os.environ.get('DYNAMODB_TABLE_NAME'),
                                "DYNAMODB_ROW_ID": id,
                                "EKS_UPDATE_KUBECONFIG": output["OutputValue"]
                            })
                            break

                    if not flag:
                        insert_and_update({
                            "eksClusterName": cluster,
                            "account": account,
                            "awsRegion": region,
                            "clusterError": "No Output Command to update Kubeconfig",
                            "isv": isv,
                            "environment": environment,
                            "version": version
                        })
            except Exception as err:
                print(err)

        print(final)
        return final

    elif 'action' in event and event['action'] == 'upgrade':
        final = []

        account = context.invoked_function_arn.split(":")[4]
        data = db.query_data_on_the_basis_of_account(account)
        latestImage = find_latest_image()

        for item in data["Items"]:
            if "clusterError" in item and item['clusterError'] != '':
                print("create ticket or send mail")
            else:
                regions = find_regions()
                tempDefenderImage = "defender_" + latestImage.replace(".", "_")

                if item['awsRegion'] in regions:
                    if "prismaDefenderVersion" not in item or item['prismaDefenderVersion'] != tempDefenderImage:
                        final.append({
                            "EKS_CLUSTER_NAME": item['eksClusterName'],
                            "REGION": item['awsRegion'],
                            "ACCOUNT": item['account'],
                            "DYNAMODB_IAM_ROLE_ARN": os.environ.get('DYNAMODB_IAM_ROLE_ARN'),
                            "DYNAMODB_TABLE_NAME": os.environ.get('DYNAMODB_TABLE_NAME'),
                            "DYNAMODB_ROW_ID": item['id'],
                            "EKS_UPDATE_KUBECONFIG": item["eksKubeconfig"],
                            "HELM_CHART_TAG": latestImage,
                            "ECR_ACCOUNT": os.environ.get('ECR_ACCOUNT')
                        })

        return final

    elif 'action' in event and event['action'] == 'checkError':
        account = context.invoked_function_arn.split(":")[4]
        data = db.query_data_on_the_basis_of_account(account)

        for item in data["Items"]:
            if "clusterError" in item and item['clusterError'] != '':
                print("create ticket or send mail")
                client = session.assume_role('sns', os.environ.get('DYNAMODB_IAM_ROLE_ARN'), 'us-west-2')
                notification = "EKS Cluster *" + item['eksClusterName'] + "* in *" + item['awsRegion'] + "* region of this account *" + item[
                    'account'] + "* having this issue *" + item['clusterError'] + "*"
                response = client.publish(
                    TargetArn=os.environ.get('SNS_ARN'),
                    Message=json.dumps({'default': notification}),
                    MessageStructure='json'
                )
                print(response)

        return {"status": "success"}
    else:
        print("wrong event data")
        return {}

￼Enter
