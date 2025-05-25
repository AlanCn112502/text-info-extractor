import hashlib
import hmac
import base64
import json
import time
import uuid
import requests

# 请将这些值替换为你的讯飞星火实际参数
APPID = "1897a6a2"
APISecret = "NDRiYWFhZThiYjlkYTQ0MjE3YTM5NzYx"
APIKey = "bb657953db266374bc681f101e36b3a8"
DOMAIN = "generalv3"  # X1模型使用generalv3
API_URL = "https://spark-api.xf-yun.com/v3.1/chat"

def get_auth_url():
    host_url = "spark-api.xf-yun.com"
    date = time.strftime('%a, %d %b %Y %H:%M:%S GMT', time.gmtime())
    signature_origin = f"host: {host_url}\ndate: {date}\nGET /v3.1/chat HTTP/1.1"
    signature_sha = hmac.new(APISecret.encode('utf-8'), signature_origin.encode('utf-8'), hashlib.sha256).digest()
    signature = base64.b64encode(signature_sha).decode('utf-8')
    authorization = f'api_key="{APIKey}", algorithm="hmac-sha256", headers="host date request-line", signature="{signature}"'
    auth_base64 = base64.b64encode(authorization.encode('utf-8')).decode('utf-8')
    url = f"{API_URL}?authorization={auth_base64}&date={date}&host={host_url}"
    return url

def call_spark_api(text: str) -> dict:
    url = get_auth_url()

    prompt = f"""
请从以下文本中提取结构化信息（语言：中文）：
文本：{text}

要求返回JSON格式，包含以下字段：
{{
  "人物": [],
  "组织": [],
  "时间": [],
  "地点": [],
  "事件": ""
}}
    """

    headers = {
        "Content-Type": "application/json"
    }

    data = {
        "header": {
            "app_id": APPID,
            "uid": str(uuid.uuid4())
        },
        "parameter": {
            "chat": {
                "domain": DOMAIN,
                "temperature": 0.5,
                "max_tokens": 1024
            }
        },
        "payload": {
            "message": {
                "text": [{"role": "user", "content": prompt}]
            }
        }
    }

    response = requests.post(url, headers=headers, data=json.dumps(data))
    res_json = response.json()

    try:
        result = res_json["payload"]["choices"]["text"][0]["content"]
        return json.loads(result)
    except Exception as e:
        raise RuntimeError(f"解析讯飞星火返回数据失败: {e}\n原始返回: {res_json}")

