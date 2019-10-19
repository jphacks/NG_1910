#!/usr/bin/env python
# coding: utf-8

from flask import Flask, request, abort, render_template
# from linebot import (
#     LineBotApi, WebhookHandler
# )
# from linebot.exceptions import (
#     InvalidSignatureError,
#     LineBotApiError
# )
# from linebot.models import (
#     MessageEvent, TextMessage, TextSendMessage,
# )
from datetime import datetime, timedelta
import os
import csv

# line_bot_api = LineBotApi(config.CHANNEL_ACCESS_TOKEN, http_client=RequestsHttpClient)
# line_bot_api = LineBotApi(os.environ['ACCESS_TOKEN'])
# handler = WebhookHandler(os.environ['CHANNEL_SECRET'])

app = Flask(__name__)

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