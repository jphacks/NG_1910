#!/usr/bin/env python
# coding: utf-8

from flask import Flask, request, abort, render_template
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError,
    LineBotApiError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)
from datetime import datetime, timedelta
import os
import csv
from __init__ import app, db

line_bot_api = LineBotApi(os.environ['ACCESS_TOKEN'])
handler = WebhookHandler(os.environ['CHANNEL_SECRET'])

app = Flask(__name__)


@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']
    # print(request.data)
    # get request body as text
    #body = request.get_data(as_text=True)
    body_data = request.get_data()
    charset = 'UTF-8'
    body = body_data.decode(charset, 'replace')
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):

    if (event.type != "message" or event.message.type != "text"):
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="{}さん！\nそのメッセージは選択できないよ".format(profile.display_name))
        )
        return 0

    message_text = event.message.text
    print(message_text)

    profile = line_bot_api.get_profile(event.source.user_id)
    user_name = profile.display_name #-> 表示名
    user_id = profile.user_id #-> ユーザーID
    profile_image_url = profile.picture_url #-> 画像のURL
    status_message = profile.status_message #-> ステータスメッセージ

    me = get_user(user_id)

    if me is None:
        # userが存在しないので、登録


    # try:
    #     m = obj_pat.search(message_text)
    #     if (url_pat.search(message_text)):
    #         data = message_text
    #         # line_bot_api.reply_message(
    #         #     event.reply_token,
    #         #     TextSendMessage(text="ありがとう{}さん！\n「{}」をQRコードにしてくるよ！\nちょっと待っててね！".format(profile.display_name, message_text)),
    #         # )
    #     elif (m):
    #         # if (m[2] in OBJ_DICT.keys()):
    #         if (m[2] in OBJ_LIST):
    #             # message_text = OBJ_DICT[m[2]]
    #             message_text = m[2]
    #             data = "https://line.me/R/ti/p/%40199vfndp?_aqr-obj={}".format(message_text)
    #             # line_bot_api.reply_message(
    #             #     event.reply_token,
    #             #     TextSendMessage(text="ありがとう{}さん！\n「{}」をQRコードにしてくるよ！\nちょっと待っててね！".format(profile.display_name, message_text)),
    #             # )
    #         else:
    #             line_bot_api.reply_message(
    #                 event.reply_token,
    #                 TextSendMessage(text="{}さん！\nそのオブジェクトは存在しないよ！！\n下の「3DオブジェクトのQRを作る」からオブジェクトを選択してね！".format(profile.display_name))
    #             )
    #             return 0
    #     else:
    #         data = "https://line.me/R/ti/p/%40199vfndp?&_aqr-message={}".format(message_text)
    #         # line_bot_api.reply_message(
    #         #     event.reply_token,
    #         #     TextSendMessage(text="ありがとう{}さん！\n「{}」をQRコードにしてくるよ！\nちょっと待っててね！".format(profile.display_name, message_text))
    #         # )

    #     colors = random.choice(color_patterns)
    #     Q = qr.QRCode()
    #     # Q = qr.QRCode(
    #     #     version=10,
    #     #     error_correction=qr.constants.ERROR_CORRECT_H,
    #     #     box_size=3,
    #     #     border=8
    #     # )
    #     Q.add_data(data)
    #     Q.make()
    #     qr_img = Q.make_image(fill_color=colors[0], back_color=colors[1])
    #     output = io.BytesIO()
    #     qr_img.save(output, format='png')
    #     qr_img_bin = output.getvalue()
    #     img_url = upload_s3(qr_img_bin)
    #     print(img_url)
    #     if not (".png" in img_url):
    #         text = "ごめんね{}さん\n「{}」のQRコード作成に失敗したよ".format(profile.display_name, message_text)
    #         img_url = fault_img
    #     else:
    #         text = "{}さん！\n「{}」のQRコードが作成できたよ！\n専用アプリで読み込んでみてね！".format(profile.display_name, message_text)

    #     # print(text)
    #     line_bot_api.reply_message(
    #         event.reply_token,
    #         [TextSendMessage(text=text), ImageSendMessage(original_content_url=img_url, preview_image_url=img_url)],
    #     )

    # except Exception as e:
    #     line_bot_api.reply_message(
    #         event.reply_token,
    #         [TextSendMessage(text = "ごめんね{}さん\n「{}」のQRコード作成に失敗したよ".format(profile.display_name, message_text)), ImageSendMessage(original_content_url=fault_img, preview_image_url=fault_img)],
    #     )
    #     raise(e)


@app.route("/<user_id>/<tag>")
def log(user_id, tag):
    now = datetime.now()
    log = []

    with open('./log.csv', 'a') as f:
        now = datetime.now()
        now_str = now.strftime('%Y-%m-%d %H:%M:%S')
        log = [user_id, tag, now_str]
        writer = csv.writer(f)
        writer.writerow(log)

    return render_template('log.html', log=log)


@app.route("/<user_id>/reset")
def reset(user_id):
    with open('./log.csv', 'w') as f:
        writer = csv.writer(f)
        writer.writerow([])

    return render_template('reset.html')


@app.route("/<user_id>")
def index(user_id):
    logs = []
    with open('./log.csv') as f:
        reader = csv.reader(f)
        logs = [row for row in reader]
        print(logs)

    return render_template('index.html', logs=logs)


# try:
#     line_bot_api.push_message('<to>', TextSendMessage(text='Hello World!'))
# except LineBotApiError as e:
#     print(str(e))
#     # error handle

if __name__ == "__main__":
    app.run()