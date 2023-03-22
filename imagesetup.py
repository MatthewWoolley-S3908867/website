import boto3
import urllib.request
import os

def imagepull():
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('music')

    response = table.scan()
    data = response['Items']
    for val in data:
        url = val['Img_url']
        filename = ("pictures" + "/" + val['Title'].replace(" ", "_") + "_Image.jpg")
        print(url)
        print(filename)
        urllib.request.urlretrieve(url, filename)


def upload():
    s3 = boto3.client('s3')
    bucket_name = "songimagemymusicsite"
    for filename in os.listdir("pictures/"):
        s3.upload_file("pictures/" + filename, bucket_name, filename)

