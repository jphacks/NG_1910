#!/usr/bin/env python
# coding: utf-8

import os
import base64
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
from linebot.models import MessageEvent, TextMessage, TextSendMessage, AudioSendMessage, ImageSendMessage, LocationSendMessage


line_bot_api = LineBotApi(os.environ['ACCESS_TOKEN'])
handler = WebhookHandler(os.environ['CHANNEL_SECRET'])


def get_me(id):
    me = db.session.query(User).filter_by(user_id=id).one_or_none()

    return me

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
    room_id = None
    if event.source.type == 'user':
        user_id = event.source.user_id
        send_to = user_id
    elif event.source.type == 'group':
        group_id = event.source.group_id
        send_to = group_id
    elif event.source.type == 'room':
        room_id = event.source.room_id
        send_to = room_id

    app.logger.debug('e_type:', e_type, event)

    if e_type == 'follow':
        # TODO: user create
        app.logger.debug('e_type: follow', user_id)
    elif e_type == 'unfollow':
        # TODO: user delete
        app.logger.debug('e_type: unfollow', user_id)
    elif e_type == 'join':
        # TODO: group create
        text = f'{Config.HOME_URL}/{send_to}/'
        push_message = TextSendMessage(text=text)
        line_bot_api.reply_message(
            event.reply_token,
            push_message,
        )
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
                text = f'{Config.HOME_URL}/{send_to}/'
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

    # profile = line_bot_api.get_profile(user_id)
    # user_name = profile.display_name  # -> 表示名
    # user_id = profile.user_id #-> ユーザーID
    # profile_image_url = profile.picture_url  # -> 画像のURL
    # status_message = profile.status_message  # -> ステータスメッセージ

    me = get_me(send_to)

    if me is None:
        # userが存在しないので、登録
        user = User(**dict(
            user_id=send_to
        ))
        db.session.add(user)
        db.session.commit()

        app.logger.debug('created!!!!!')

    # except Exception as e:
    #     line_bot_api.reply_message(
    #         event.reply_token,
    #         [TextSendMessage(text = "ごめんね{}さん\n「{}」のQRコード作成に失敗したよ".format(profile.display_name, message_text)), ImageSendMessage(original_content_url=fault_img, preview_image_url=fault_img)],
    #     )
    #     raise(e)
    return 'OK'


@app.route("/<id>/<contents>")
def log(id, contents):
    me = get_me(id)
    if me is None:
        abort(404)

    now = datetime.now()
    log = Log(**dict(
        user_id=id,
        contents=contents
    ))
    db.session.add(log)
    db.session.commit()

    try:
        test = f'user_id: {id}\ncontents: {contents}'
        app.logger.debug('ok', test)
        line_bot_api.push_message(
            id,
            TextSendMessage(text=test)
        )
    except LineBotApiError as e:
        app.logger.debug(str(e))
        # error handle
    return 'OK'


# @app.route("/<user_id>/reset")
# def reset(user_id):
#     me = get_me(user_id)
#     if me is None:
#         abort(404)

#     user_id = "Ud8f78f7c6a6377ca00790e0a10197e06"
#     try:
#         test = f'page: user_page, : {user_id}'
#         app.logger.debug('ok', test)
#         line_bot_api.push_message(
#             user_id,
#             TextSendMessage(text=test)
#         )
#     except LineBotApiError as e:
#         app.logger.debug(str(e))
#         # error handle
#     return


@app.route("/<id>", methods=['GET', 'POST'])
def user_page(id):
    now = datetime.now()
    # app.logger.debug(request.__dict__)
    # app.logger.debug(request.get_json(force=True))
    json_data = request.get_json(force=True)

    # 存在してほしい値だけとる
    json_data = validate_json(json_data)
    if len(json_data) == 0:
        app.logger.debug('not posted')
        return

    name = json_data.get('name')
    name = 'ゲスト' if name is None else name
    lat = float(json_data.get('lat'))
    lon = float(json_data.get('lon'))
    address = json_data.get('address')
    message = json_data.get('message')
    image_base64 = json_data.get('image')
    audio_base64 = json_data.get('audio')

    if image_base64 is not None:
        destination_blob_name = now.strftime('%Y%m%d%H%M%S')
        content_type = 'png'
        file_blob = base64.b64decode(image_base64)

        image_url = upload_file(
            file_blob,
            destination_blob_name,
            content_type
        )

    if audio_base64 is not None:
        # TODO: ここでaudioのbase64 -> wav or mp3へ変換したい
        # destination_blob_name = now.strftime('%Y%m%d%H%M%S')
        # content_type = 'wav'
        # file_blob = base64.b64decode(image_base64)

        # image_url = upload_file(
        #     file_blob,
        #     destination_blob_name,
        #     content_type
        # )
        audio_url = 'sample.mp3'

    app.logger.info(image_url)

    me = get_me(id)
    if me is None:
        abort(404)

    try:
        test = f'{name}さんからメッセージが届きました'
        message_list = []
        if (lat is not None) and (lon is not None) and (address is not None):
            message_list += [
                LocationSendMessage(
                    title='{name}さんの現在地',
                    address=address,
                    latitude=lat,
                    longitude=lon
                )
            ]
        if message is not None:
            message_list += [
                TextSendMessage(
                    text=message
                )
            ]
        if image_base64 is not None:
            message_list += [
                ImageSendMessage(
                    originalContentUrl=image_url,
                    previewImageUrl=image_url
                )
            ]
        if audio_base64 is not None:
            # message_list += [
            #     AudioSendMessage(
            #         originalContentUrl=audio_url,
            #         duration=audio_duration
            #     )
            # ]
            pass

        app.logger.debug('ok', test)
        line_bot_api.push_message(
            id,
            message_list
        )
    except LineBotApiError as e:
        app.logger.debug(str(e))
        # error handle
    return 'OK'


if __name__ == "__main__":
    app.run()
