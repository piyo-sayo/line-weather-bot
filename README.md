# 🌤️ LINE Weather Bot

AWS Lambda + API Gateway + DynamoDB を使って作成した LINE 天気通知 Bot です。  
ユーザーが地域を登録すると、毎朝その地域の天気を自動で通知します。

---

## 🧠 使用技術
- AWS Lambda (Python 3.12)
- API Gateway
- DynamoDB
- CloudWatch Events
- LINE Messaging API
- AWS CDK (Python)

---

## 🚀 デプロイ構成
1. `lambda/webhook`：LINEからのWebhookを受け取り
2. `lambda/send_weather`：毎朝の天気通知処理
3. `cdk`：AWS CDKによるIaC構成

---

## 📱 機能概要
- 初回起動時に地域をQuick Replyで選択  
- DynamoDBにユーザー地域を保存  
- 毎朝自動で天気をPush通知  

---

## 📊 アーキテクチャ構成図
ユーザー（LINE）
↓ Webhook
API Gateway
↓
Lambda（webhook） ─→ DynamoDB（ユーザー地域保存）
↑ ↓
└── CloudWatch Event → Lambda（send_weather）
↓
LINE Push通知

---

## ✨ 作成者
**Sayo.W**（[@piyo-sayo](https://github.com/piyo-sayo)）
