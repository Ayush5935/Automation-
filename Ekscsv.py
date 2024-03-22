import boto3
import subprocess

def main():
    region = 'us-east-1'
    session = boto3.Session(region_name=region)

    eks = session.client('eks')
    cfn = session.client('cloudformation')
    clusters = eks.list_clusters()

    for cluster_name in clusters["clusters"]:
        try:
            result = eks.describe_cluster(name=cluster_name)
            if "tags" not in result['cluster']:
                continue
            if "dish:deployment:stack-name" not in result['cluster']["tags"]:
                continue
            stacks = cfn.describe_stacks(StackName=result['cluster']["tags"]['dish:deployment:stack-name'])
            if len(stacks['Stacks']) == 0:
                continue
            if "Outputs" not in stacks['Stacks'][0]:
                continue
            flag = True
            for output in stacks["Stacks"][0]["Outputs"]:
                if output["OutputKey"] == "EKSClusteraddClusterConfigCommand8D1DE1D0":
                    flag = False
                    bashCommand = output["OutputValue"]
                    process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
                    out, error = process.communicate()
                    print(out, error)
                    if error is None:
                        # Add helm installation command here
                        helm_command = "helm install cloudability-metrics-agent --set apiKey=GJvw6KQ1Hj6TqPWo3EC3Z1j4Vb2M5De91Qu7cs0x --set clusterName=rd-ndc-eks-cluster-prod-radcom-be-13-5 metrics-agent/ -n cloudability --create-namespace"
                        subprocess.run(helm_command, shell=True)
                    else:
                        print(error)
                    break
            if flag:
                print("No Output Command to update Kubeconfig")
        except Exception as err:
            print(err)

if __name__ == "__main__":
    main()
￼Enter
