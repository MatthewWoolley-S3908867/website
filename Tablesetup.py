import boto3
import json
def makemusictable():
    dynamodb = boto3.client('dynamodb')
    table = dynamodb.create_table(
    TableName='music',
        KeySchema=[
            {
                'AttributeName': 'Title',
                'KeyType': 'HASH'
            },
            {
                'AttributeName': 'Artist',
                'KeyType': 'RANGE'
            }
        ],
        AttributeDefinitions=[
            {
                'AttributeName': 'Title',
                'AttributeType': 'S'
            },
            {
                'AttributeName': 'Artist',
                'AttributeType': 'S'
            }
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 10,
            'WriteCapacityUnits': 10
        }

    )
    print(table)

def filltable():
    dynamodb = boto3.client('dynamodb')
    file = open('a1.json', 'r')
    data = json.load(file)['songs']
    for item in data:
        dynamodb.put_item(
            TableName='music',
            Item={
                    'Title': {'S': item['title']},
                    'Artist': {'S': item['artist']},
                    'Year': {'S': item['year']},
                    'Web_url': {'S': item['web_url']},
                    'Img_url': {'S': item['img_url']}
                }
        )
    print("full")

#makemusictable()
#print("tablemade")
#filltable()
