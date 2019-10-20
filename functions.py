import os
import boto3
import random
import string
import re

session = boto3.session.Session(aws_access_key_id=os.environ["S3_ACCESS_KEY"],
                                aws_secret_access_key=os.environ["S3_SECRET_KEY"],
                                region_name=os.environ["S3_REGION_NAME"])
client = session.client('s3')


def get_random_name(n):
    randlst = [
        random.choice(
            string.ascii_letters +
            string.digits) for i in range(n)]
    return ''.join(randlst)


def upload_s3(image_binary, image_name):

    try:
        client.put_object(
            ACL="public-read",
            Body=image_binary,
            Bucket=os.environ["S3_BUCKET_NAME"],
            Key=image_name)
        url = "https://s3-{0}.amazonaws.com/{1}/{2}".format(
            os.environ['S3_REGION_NAME'],
            os.environ["S3_BUCKET_NAME"],
            image_name
        )
        return url

    except Exception as e:
        print("S3!!!!!!!!!!!!!!!!!!!!!")
        raise(e)

    # upload_filename = os.path.join(folder_name, upload_filename)
    # try:
    #     result = s3.upload_file(original_file_path, os.environ["S3_BUCKET_NAME"], upload_filename, ExtraArgs={"ContentType": "image/png", 'ACL':'public-read'})
    # except boto3.exceptions.S3UploadFailedError:
    #     print("S3へのアップロードでエラーが発生しました")
    #     raise boto3.exceptions.S3UploadFailedError
    # finally:
    #     # 後片付け
    #     pass

# url_pat = re.compile('^(http|https)://([\w\-]+\.)+[\w\-]+(/[\w\-./?%&=]*)?$')
# obj_pat = re.compile('^(<obj:)(.+)(>)$')

# def check_session(user_id, message_text):
#     path = "session/{}_session.log".format(user_id)
#     if (os.path.exists(path)):
#         f = open(path, "r", encoding="utf-8")
#         f_c = dict([element.split(":") for element in f.read().split()])
#         if (f_c["obj"] != "_")
#         if (url_pat.search(message_text)):
#             f.close()
#             f = open(path, "w", encoding="utf-8")
#         return f_c
#     else:
#         f = open(path, "w", encoding="utf-8")
#         if (url_pat.search(message_text)):
#             line = "obj:_,url:{},status:{}".format(message_txt, 2)
#         else:
#             m = obj_pat.search(message_text)
#             # if (m[2] in OBJ_DICT.keys()):
#             if (m[2] in OBJ_LIST):
#                 # message_text = OBJ_DICT[m[2]]
#                 message_text = m[2]
#                 data = "https://line.me/R/ti/p/%40199vfndp?_aqr-obj={}".format(message_text)
#                 # line_bot_api.reply_message(
#                 #     event.reply_token,
#                 #     TextSendMessage(text="ありがとう{}さん！\n「{}」をQRコードにしてくるよ！\nちょっと待っててね！".format(profile.display_name, message_text)),
#                 # )
#             else:
#                 line_bot_api.reply_message(
#                     event.reply_token,
#                     TextSendMessage(text="{}さん！\nそのオブジェクトは存在しないよ！！\n下の「3DオブジェクトのQRを作る」からオブジェクトを選択してね！".format(profile.display_name))
#                 )
#                 return 0
#         else:
#             data = "https://line.me/R/ti/p/%40199vfndp?&_aqr-message={}".format(message_text)
#             # line_bot_api.reply_message(
#             #     event.reply_token,
#             #     TextSendMessage(text="ありがとう{}さん！\n「{}」をQRコードにしてくるよ！\nちょっと待っててね！".format(profile.display_name, message_text))
#                 # )
#         f.write("obj:_,url:_,status:_")
#         f.close()
