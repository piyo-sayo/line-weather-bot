import os, json, boto3
from urllib import request as urlreq

DDB = boto3.resource("dynamodb").Table(os.environ["TABLE_NAME"])
LINE_TOKEN = os.environ["LINE_TOKEN"]

# 主要都市リスト
AREAS = {
    "高松": ("Takamatsu", 34.342, 134.046),
    "東京": ("Tokyo", 35.676, 139.650),
    "大阪": ("Osaka", 34.693, 135.502),
    "神戸": ("Kobe", 34.690, 135.195),
    "福岡": ("Fukuoka", 33.590, 130.401),
    "札幌": ("Sapporo", 43.062, 141.354),
    "松山": ("Matsuyama", 33.839, 132.765),
    "静岡": ("Shizuoka", 34.975, 138.382),
    "船橋": ("Funabashi", 35.694, 139.983),
}

def handler(event, context):
    """LINE Webhook エントリポイント"""
    body = json.loads(event.get("body", "{}"))
    events = body.get("events", [])
    if not events:
        return {"statusCode": 200, "body": "no events"}

    ev = events[0]
    reply_token = ev.get("replyToken")
    user_id = ev.get("source", {}).get("userId")
    text = ev.get("message", {}).get("text", "").strip()

    # 地域が選ばれた場合
    if text in AREAS:
        label, lat, lon = AREAS[text]
        # DynamoDBに保存
        DDB.put_item(Item={
            "user_id": user_id,
            "region": label,
            "lat": str(lat),
            "lon": str(lon)
        })
        send_reply(reply_token, f"{text} を登録しました！これから毎朝お届けします☀️")
        return {"statusCode": 200, "body": "ok"}

    # 初回または未知の入力
    send_quick_reply(reply_token)
    return {"statusCode": 200, "body": "ok"}


def send_reply(reply_token, text):
    """通常メッセージを返信"""
    url = "https://api.line.me/v2/bot/message/reply"
    headers = {
        "Authorization": f"Bearer {LINE_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {"replyToken": reply_token, "messages": [{"type": "text", "text": text}]}
    data = json.dumps(payload).encode("utf-8")

    req = urlreq.Request(url, data=data, headers=headers, method="POST")
    with urlreq.urlopen(req, timeout=10) as res:
        _ = res.read().decode("utf-8")  # レスポンスは特に使わない


def send_quick_reply(reply_token):
    """Quick Reply で地域を選択させる"""
    url = "https://api.line.me/v2/bot/message/reply"
    headers = {
        "Authorization": f"Bearer {LINE_TOKEN}",
        "Content-Type": "application/json"
    }
    items = []
    for jp in ["高松", "東京", "大阪", "神戸", "福岡", "札幌", "松山", "静岡", "船橋"]:
        items.append({"type": "action", "action": {"type": "message", "label": jp, "text": jp}})
    payload = {
        "replyToken": reply_token,
        "messages": [{
            "type": "text",
            "text": "地域を選んでください👇",
            "quickReply": {"items": items}
        }]
    }

    data = json.dumps(payload).encode("utf-8")
    req = urlreq.Request(url, data=data, headers=headers, method="POST")
    with urlreq.urlopen(req, timeout=10) as res:
        _ = res.read().decode("utf-8")
# def handler(event, context):
#     print("EVENT:", json.dumps(event))
#     return {
#         "statusCode": 200,
#         "body": "ok"
#     }