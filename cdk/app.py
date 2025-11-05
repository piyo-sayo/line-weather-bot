#!/usr/bin/env python3
import aws_cdk as cdk
from stacks.bot_stack import BotStack  # ← ここが新しい参照先

app = cdk.App()
BotStack(app, "BotStack")
app.synth()
