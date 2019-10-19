#!/usr/bin/env python
# coding: utf-8

import csv
import os
from datetime import datetime, timedelta


try:
    from flask_app import app, db
    from flask_app.models import *
    from flask_app.config import Config
except BaseException:
    from flask_app import app, db
    from flask_app.models import *
    from flask_app.config import Config
from flask import Flask, abort, render_template, request
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import MessageEvent, TextMessage, TextSendMessage


line_bot_api = LineBotApi(os.environ['ACCESS_TOKEN'])
handler = WebhookHandler(os.environ['CHANNEL_SECRET'])


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
    send_to = None
    user_id = None
    group_id = None
    if event.source.type == 'user':
        user_id = event.source.user_id
        send_to = user_id
    else:
        group_id = event.source.group_id
        send_to = group_id

    app.logger.debug('e_type:', e_type, event)

    if e_type == 'follow':
        # TODO: user create
        app.logger.debug('e_type: follow', user_id)
    elif e_type == 'unfollow':
        # TODO: user delete
        app.logger.debug('e_type: unfollow', user_id)
    elif e_type == 'join':
        # TODO: group create
        app.logger.debug('e_type: join', group_id)
    elif e_type == 'leave':
        # TODO: group delete
        app.logger.debug('e_type: leave', group_id)
    elif e_type == "message":
        m_type = event.message.type
        push_message = None

        if m_type == "text":
            message_text = event.message.text
            if message_text == 'URL':
                text = f'{Config.HOME_URL}/{send_to}'
                push_message = TextSendMessage(text=text)
            else:
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


@app.route("/<user_id>/<contents>")
def log(user_id, contents):
    me = get_user(user_id)
    if me is None:
        abort(404)

    now = datetime.now()
    log = Log(**dict(
        user_id=user_id,
        contents=contents
    ))
    db.session.add(log)
    db.session.commit()

    user_id = "Ud8f78f7c6a6377ca00790e0a10197e06"
    try:
        test = f'user_id: {user_id}\ncontents: {contents}'
        app.logger.debug('ok', test)
        line_bot_api.push_message(
            'user_id',
            TextSendMessage(text=test)
        )
    except LineBotApiError as e:
        app.logger.debug(str(e))
        # error handle
    return


# @app.route("/<user_id>/reset")
# def reset(user_id):
#     me = get_user(user_id)
#     if me is None:
#         abort(404)

#     user_id = "Ud8f78f7c6a6377ca00790e0a10197e06"
#     try:
#         test = f'page: user_page, : {user_id}'
#         app.logger.debug('ok', test)
#         line_bot_api.push_message(
#             'user_id',
#             TextSendMessage(text=test)
#         )
#     except LineBotApiError as e:
#         app.logger.debug(str(e))
#         # error handle
#     return


@app.route("/<user_id>")
def user_page(user_id):
    me = get_user(user_id)
    if me is None:
        abort(404)

    user_id = "Ud8f78f7c6a6377ca00790e0a10197e06"
    try:
        test = f'page: user_page, : {user_id}'
        app.logger.debug('ok', test)
        line_bot_api.push_message(
            'user_id',
            TextSendMessage(text=test)
        )
    except LineBotApiError as e:
        app.logger.debug(str(e))
        # error handle
    return


if __name__ == "__main__":
    app.run()
