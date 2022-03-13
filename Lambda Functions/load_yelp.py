# !pip install boto3

import boto3
import json
import datetime
import csv
from decimal import Decimal
from dotenv import load_dotenv
import requests

load_dotenv()

AWS_ACCESS_KEYID = os.getenv('AWS_ACCESS_KEYID')
SECRET_KEY = os.getenv('SERVICE_ACCOUNT_FILE')
REGION = os.getenv('REGION')
session = boto3.Session(aws_access_key_id=AWS_ACCESS_KEYID,aws_secret_access_key=SECRET_KEY,region_name=REGION)

client = session.resource('dynamodb')
table = client.Table('yelp_restaurants')

API_KEY = os.getenv('API_KEY')
ENDPOINT = 'https://api.yelp.com/v3/businesses/search'
HEADERS = {'Authorization': 'bearer %s' % API_KEY}

cuisine_types = ['chinese','mexican','italian','thai','japanese','french'] 
for cuisine_type in cuisine_types:
    offset = 0
    for i in range(20):
        offset += 50
        PARAMETERS = {
            'term': 'restaurant',
            'location': 'Manhattan',
            'categories': cuisine_type,
            'limit': 50,
            'offset': offset
        }
        response = requests.get(url=ENDPOINT, params=PARAMETERS, headers=HEADERS)
        business_data = response.json()
        try:
            for biz in business_data['businesses']:

                    table.put_item(
                        Item={
                            'business_id': biz['id'],
                            'name': biz['name'],
                            'category': biz['categories'][0]['alias'],
                            'address': biz['location']['address1'],
                            'city': biz['location']['city'],
                            'zipcode': biz['location']['zip_code'],
                            'reviewCount': biz['review_count'],
                            'rating': Decimal(str(biz['rating'])),
                            'insertedAtTimestamp': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        },
                        ConditionExpression='attribute_not_exists(businessId) AND attribute_not_exists(insertedAtTimestamp)'
                    )
        except Exception as e:
            print(e)
            continue
    # print(offset)


