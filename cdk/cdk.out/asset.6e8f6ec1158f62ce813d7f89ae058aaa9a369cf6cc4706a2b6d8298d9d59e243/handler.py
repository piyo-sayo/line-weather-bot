import os, json, boto3
from urllib import request as urlreq

DDB = boto3.resource("dynamodb").Table(os.environ["TABLE_NAME"])
LINE_TOKEN = os.environ["LINE_TOKEN"]

def handler(event, context):
    # 全ユーザー取得（少数前提。多くなったらLastEvaluatedKeyでページング）
    res = DDB.scan()
    items = res.get("Items", [])
    for it in items:
        user_id = it["user_id"]
        region = it.get("region", "Tokyo")
        lat = float(it.get("lat", "35.676"))
        lon = float(it.get("lon", "139.650"))

        text = build_weather_text(region, lat, lon)
        push_line(user_id, text)

    return {"statusCode": 200, "body": f"sent:{len(items)}"}

def build_weather_text(region, lat, lon):
    """Open-Meteo APIで天気データを取得"""
    url = (
        "https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}&longitude={lon}"
        "&daily=temperature_2m_max,temperature_2m_min"
        "&timezone=Asia%2FTokyo"
    )

    with urlreq.urlopen(url, timeout=10) as res:
        r = json.loads(res.read().decode("utf-8"))

    max_t = r["daily"]["temperature_2m_max"][0]
    min_t = r["daily"]["temperature_2m_min"][0]
    return f"{region} の今日の天気\n最高: {max_t}℃ / 最低: {min_t}℃"

def push_line(user_id, text):
    """LINE Push APIでメッセージ送信"""
    url = "https://api.line.me/v2/bot/message/push"
    headers = {
        "Authorization": f"Bearer {LINE_TOKEN}",
        "Content-Type": "application/json"
    }
    body = {"to": user_id, "messages": [{"type": "text", "text": text}]}
    data = json.dumps(body).encode("utf-8")

    req = urlreq.Request(url, data=data, headers=headers, method="POST")
    with urlreq.urlopen(req, timeout=10) as res:
        _ = res.read().decode("utf-8")  # レスポンス内容は使わない
