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
