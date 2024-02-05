from aws_cdk import (
    aws_codebuild as codebuild,
    aws_events as events,
    aws_events_targets as targets,
    aws_s3 as s3,
    core,
)

class MyHelmChartVersioningStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # S3 bucket for Helm charts
        bucket = s3.Bucket(self, "HelmChartBucket")

        # CodeBuild project
        codebuild.Project(
            self, "HelmChartBuild",
            source=codebuild.Source.s3(bucket=bucket, path="path/to/source.zip"),
            build_spec=codebuild.BuildSpec.from_source_filename("buildspec.yml"),
            environment=codebuild.BuildEnvironment(
                build_image=codebuild.LinuxBuildImage.STANDARD_4_0
            )
        )

        # S3 event rule to trigger CodeBuild directly
        rule = events.Rule(
            self, "HelmChartRule",
            event_pattern={
                "source": ["aws.s3"],
                "detail": {
                    "eventName": ["PutObject"]
                },
                "resources": [bucket.bucket_arn],
            }
        )
        rule.add_target(targets.CodeBuildProject(
            project=codebuild.Project.from_project_name(self, "CodeBuildProject", "HelmChartBuild"))
        )

app = core.App()
MyHelmChartVersioningStack(app, "MyHelmChartVersioningStack")
app.synth()
￼Enter
