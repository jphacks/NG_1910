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
from models import *

line_bot_api = LineBotApi(os.environ['ACCESS_TOKEN'])
handler = WebhookHandler(os.environ['CHANNEL_SECRET'])

app = Flask(__name__)


def get_user(user_id):
    me = db.session.query(User).filter_by(user_id=user_id).one_or_none()

    return me


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

    e_type = event.type
    user_id = event.source.user_id

    if e_type == 'follow':
        # TODO: user create
        app.logger.debug('e_type: follow', user_id)
    elif e_type == 'unfollow':
        # TODO: user delete
        app.logger.debug('e_type: unfollow', user_id)
    elif e_type == 'join':
        # TODO: group create
        group_id = event.source.group_id
        app.logger.debug('e_type: join', group_id)
    elif e_type == 'leave':
        # TODO: group delete
        group_id = event.source.group_id
        app.logger.debug('e_type: leave', group_id)
    elif e_type == "message":
        m_type = event.message.type
        push_message = None

        if m_type == "text":
            message_text = event.message.text
            push_message = TextSendMessage(text=message_text)
        elif m_type == 'image':
            pass
            # ImageSendMessage
        elif m_type == 'audio':
            pass
        elif m_type == 'location':
            pass
        elif m_type == 'sticker':
            pass

        if push_message is None:
            app.logger.debug('m_type:', m_type, 'not text')
        else:
            app.logger.debug('m_type:', m_type, 'text ok')
            line_bot_api.reply_message(
                event.reply_token,
                push_message,
            )
    return

    if (event.type != "message" or event.message.type != "text"):
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(
                text="{}さん！\nそのメッセージは選択できないよ".format(profile.display_name))
        )
        return 0

    message_text = event.message.text
    print(message_text)

    profile = line_bot_api.get_profile(user_id)
    user_name = profile.display_name  # -> 表示名
    # user_id = profile.user_id #-> ユーザーID
    profile_image_url = profile.picture_url  # -> 画像のURL
    status_message = profile.status_message  # -> ステータスメッセージ

    me = get_user(user_id)

    if me is None:
        # userが存在しないので、登録
        user = User(**dict(
            user_id=user_id,
            user_name=user_name,
            profile_image_url=profile_image_url
        ))

    # except Exception as e:
    #     line_bot_api.reply_message(
    #         event.reply_token,
    #         [TextSendMessage(text = "ごめんね{}さん\n「{}」のQRコード作成に失敗したよ".format(profile.display_name, message_text)), ImageSendMessage(original_content_url=fault_img, preview_image_url=fault_img)],
    #     )
    #     raise(e)


@app.route("/<user_id>/<tag>")
def log(user_id, tag):
    me = get_user(user_id)
    if me is None:
        abort(404)

    now = datetime.now()
    log = Log(**dict(
        user_id=user_id,
        tag=tag
    ))
    db.session.add(log)
    db.session.commit()

    return


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
