from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, AudioSendMessage, ImageSendMessage, LocationSendMessage
import os
import base64
import io

# Base64でエンコードされたファイルのパス
target_file = "image.txt"
# デコードされた画像の保存先パス
image_file = "decode.jpg"

with open(target_file, 'rb') as f:
    img_base64 = f.read()

with open(image_file, "wb") as f:
    f.write(img_base64)

#バイナリデータ <- base64でエンコードされたデータ

img_binary = base64.b64decode(img_base64)

line_bot_api = LineBotApi(os.environ['ACCESS_TOKEN'])
handler = WebhookHandler(os.environ['CHANNEL_SECRET'])


send_to = 'Ra25b2653c86f146b0c79d141ee8040b5'

# line_bot_api.push_message(
#     send_to,
#     TextSendMessage(text=test)
# )


# [START upload_file]
def upload_file(file_stream, filename, content_type):
    client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(filename)

    blob.upload_from_string(
        file_stream,
        content_type=content_type)

    url = blob.public_url

    return url


destination_blob_name = 'test'
content_type = 'png'
file_blob = image_binary

public_url = upload_file(
    file_blob,
    destination_blob_name,
    content_type
)
