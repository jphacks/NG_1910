#!/usr/bin/env python
# coding: utf-8

import io
import dropbox
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


ALLOW_PARAMS = ['name', 'message', 'lat', 'lon', 'address', 'image']

line_bot_api = LineBotApi(os.environ['ACCESS_TOKEN'])
handler = WebhookHandler(os.environ['CHANNEL_SECRET'])


def get_me(id):
    me = db.session.query(User).filter_by(user_id=id).one_or_none()

    return me


def upload_image(img_binary, file_name):

    ACCESS_TOKEN = os.environ["D_ACCESS_TOKEN"]
    dbx = dropbox.Dropbox(ACCESS_TOKEN)
    path = '/static/image/' + file_name

    dbx.files_upload(img_binary, path)

    setting = dropbox.sharing.SharedLinkSettings(
        requested_visibility=dropbox.sharing.RequestedVisibility.public)
    link = dbx.sharing_create_shared_link_with_settings(
        path=path, settings=setting)

    links = dbx.sharing_list_shared_links(path=path, direct_only=True).links
    if links is not None:
        for link in links:
            url = link.url
            url = url.replace(
                'www.dropbox',
                'dl.dropboxusercontent').replace(
                '?dl=0',
                '')
            return url


def validate_json(json_data):
    return_json = {}
    for key, value in json_data.items():
        if key in ALLOW_PARAMS:
            return_json[key] = value

    return return_json


@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']
    # print(request.data)
    # get request body as text
    # body = request.get_data(as_text=True)
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

    me = get_me(send_to)
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
            elif message_text == '履歴':
                if len(me.logs) == 0:
                    text = '履歴なし'
                else:
                    text = '[履歴]\n'
                    for log in me.logs:
                        time = log.created_at.strftime('%Y/%m/%d %H-%M-%S')
                        text += f'\n{time}:\n{log.contents}\n'
                push_message = TextSendMessage(text=text)
            elif message_text == '履歴削除':
                text = '本当に削除しますか？(yes/no)'
                push_message = TextSendMessage(text=text)
            elif message_text == 'yes':
                me.logs = []
                db.session.add(me)
                db.session.commit()

                push_message = TextSendMessage(text="削除完了")
            elif message_text == 'NFC':
                url = f'{Config.HOME_URL}/{send_to}/'
                text = f'ショートカットへ以下のURLをトリガーに設定してください'
                push_message = [
                    TextSendMessage(
                        text=text), TextSendMessage(
                        text=url)]
            elif message_text == '使い方':
                text = '使い方:\n工事中'
                push_message = TextSendMessage(text=text)
            else:
                push_message = TextSendMessage(text="無効なメッセージです")
        elif m_type == 'image':
            pass
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

    if me is None:
        # userが存在しないので、登録
        user = User(**dict(
            user_id=send_to
        ))
        db.session.add(user)
        db.session.commit()

        app.logger.debug('created!!!!!')

    return 'OK'


@app.route("/<id>", methods=['GET', 'POST'])
def user_page(id):
    now = datetime.now()
    json_data = request.get_json(force=True)

    # 存在してほしい値だけとる
    json_data = validate_json(json_data)
    app.logger.debug(str([str(f'{k},{v}') for k, v in json_data.items()]))

    if len(json_data) == 0:
        app.logger.debug('not posted')
        return

    name = json_data.get('name')
    name = 'ゲスト' if name is None else name
    lon = json_data.get('lon')
    lon = 135.26172618 if lon is None else float(lon)
    lat = json_data.get('lat')
    lat = 36.27791617 if lat is None else float(lat)
    address = json_data.get('address')
    message = json_data.get('message')
    image_base64 = json_data.get('image')
    audio_base64 = json_data.get('audio')

    if message is not None:
        log = Log(**dict(
            user_id=id,
            contents=message
        ))
    db.session.add(log)
    db.session.commit()

    image_url = ''
    audio_url = ''

    try:
        if image_base64 is not None:
            destination_blob_name = now.strftime('%Y%m%d%H%M%S')
            content_type = 'png'

            file_blob = base64.b64decode(image_base64)

            # image_url = upload_file(
            #     file_blob,
            #     destination_blob_name,
            #     content_type
            # )

            file_name = f'{destination_blob_name}.{content_type}'
            image_url = upload_image(file_blob, file_name)
            app.logger.debug('image saved', image_url)

    except Exception as e:
        app.logger.warn(str(e))

    try:
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
            # audio_url = 'sample.mp3'
            pass

    except Exception as e:
        app.logger.warn(str(e))

    app.logger.info(image_url)

    me = get_me(id)
    if me is None:
        app.logger.warn('me is None')

    try:

        message_list = []
        # test = f'{name}さんからメッセージが届きました'
        # message_list += [
        #     TextSendMessage(
        #         text=test
        #     )
        # ]
        if (lat is not None) and (lon is not None) and (address is not None):
            message_list += [
                LocationSendMessage(
                    title=f'{name}さんの現在地',
                    address=address,
                    latitude=lat,
                    longitude=lon
                )
            ]
        if message is not None:
            message = f'メッセージ:\n{message}'
            message_list += [
                TextSendMessage(
                    text=message
                )
            ]
        if image_base64 is not None:
            message_list += [
                ImageSendMessage(
                    original_content_url=image_url,
                    preview_image_url=image_url
                )
            ]
        if audio_base64 is not None:
            # message_list += [
            #     AudioSendMessage(
            #         original_content_url=audio_url,
            #         duration=2000
            #     )
            # ]
            pass

        app.logger.debug('ok')
        line_bot_api.push_message(
            id,
            message_list
        )
    except LineBotApiError as e:
        app.logger.debug(str(e))
        # error handle
    except Exception as e:
        app.logger.warn(str(e))

    return 'OK'


if __name__ == "__main__":
    app.run()
