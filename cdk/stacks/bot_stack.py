import os
from aws_cdk import (
    Stack,
    Duration,
    aws_lambda as _lambda,
    aws_apigateway as apigw,
    aws_dynamodb as ddb,
    aws_events as events,
    aws_events_targets as targets,
    aws_iam as iam,
    CfnParameter,
)
from constructs import Construct

class BotStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs):
        super().__init__(scope, construct_id, **kwargs)

        # === DynamoDB: user_id → region ===
        table = ddb.Table(
            self, "UserRegionTable",
            partition_key=ddb.Attribute(name="user_id", type=ddb.AttributeType.STRING),
            billing_mode=ddb.BillingMode.PAY_PER_REQUEST
        )

        line_token_param = CfnParameter(
            self, "LineChannelAccessToken",
            type="String",
            description="LINE Messaging API channel access token"
        )

        webhook_fn = _lambda.Function(
            self, "WebhookHandler",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="handler.handler",
            code=_lambda.Code.from_asset("lambda/webhook"),
            timeout=Duration.seconds(15),
            environment={
                "TABLE_NAME": table.table_name,
                "LINE_TOKEN": line_token_param.value_as_string,
            }
        )
        table.grant_read_write_data(webhook_fn)

        api = apigw.RestApi(
            self, "LineWebhookApi",
            rest_api_name="line-webhook-api",
            deploy_options=apigw.StageOptions(stage_name="prod"),
        )
        webhook_res = api.root.add_resource("webhook")
        webhook_res.add_method("POST", apigw.LambdaIntegration(webhook_fn))

        send_fn = _lambda.Function(
            self, "SendWeather",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="handler.handler",
            code=_lambda.Code.from_asset("lambda/send_weather"),
            timeout=Duration.seconds(30),
            environment={
                "TABLE_NAME": table.table_name,
                "LINE_TOKEN": line_token_param.value_as_string,
            }
        )
        table.grant_read_data(send_fn)

        for fn in (webhook_fn, send_fn):
            fn.add_to_role_policy(iam.PolicyStatement(
                actions=["logs:CreateLogGroup","logs:CreateLogStream","logs:PutLogEvents"],
                resources=["*"]
            ))

        rule = events.Rule(
            self, "MorningRule",
            schedule=events.Schedule.cron(minute="0", hour="22") 
        )
        rule.add_target(targets.LambdaFunction(send_fn))