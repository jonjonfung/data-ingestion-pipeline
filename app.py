import aws_cdk as cdk
from infra.stack import EtoroPipelineStack

app = cdk.App()
EtoroPipelineStack(app, "EtoroPipelineStack",
    env=cdk.Environment(region="ap-southeast-2"))
app.synth()
