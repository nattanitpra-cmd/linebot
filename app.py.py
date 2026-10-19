import os
import sys
from flask import Flask, request, abort

from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import (
    Configuration, ApiClient, MessagingApi,
    ReplyMessageRequest, TextMessage
)
from linebot.v3.webhooks import MessageEvent, TextMessageContent

app = Flask(__name__)

# ดึงค่า Environment Variables พร้อมตรวจสอบ
channel_secret = os.environ.get("LINE_CHANNEL_SECRET")
channel_access_token = os.environ.get("LINE_CHANNEL_ACCESS_TOKEN")

if channel_secret is None or channel_access_token is None:
    print("Error: กรุณาตั้งค่า LINE_CHANNEL_SECRET และ LINE_CHANNEL_ACCESS_TOKEN ใน Environment Variables")
    sys.exit(1)

handler = WebhookHandler(channel_secret)
config = Configuration(access_token=channel_access_token)

@app.route("/")
def home():
    return "LINE Webhook is running"

@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers.get("X-Line-Signature", "")
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("Invalid signature. Please check your channel secret.")
        abort(400)
    except Exception as e:
        print(f"Error handling event: {e}")
        abort(500)

    return "OK"

@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    with ApiClient(config) as api_client:
        api = MessagingApi(api_client)
        
        # ข้อความที่ผู้ใช้ส่งมา
        user_message = event.message.text
        
        api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[
                    TextMessage(
                        text=f"สวัสดีครับ LINE Bot ทำงานแล้ว\nคุณพูดว่า: {user_message}"
                    )
                ]
            )
        )

if __name__ == "__main__":
    # สามารถเปิด debug=True ในระหว่างพัฒนาเพื่อดู Error Log ชัดเจนขึ้น
    app.run(port=5000, debug=True)