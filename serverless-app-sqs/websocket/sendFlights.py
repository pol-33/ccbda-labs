import json
import boto3
import time
import os
from dotenv import load_dotenv
from FlightRadar24 import FlightRadar24API
import logging


def reset():
    message = json.dumps({
        'type': 'reset',
        'center': CENTER,
        'bounds': [TOP_LEFT, BOTTOM_RIGHT],
    })
    dynamodb = boto3.client('dynamodb',
                            region_name=AWS_REGION)
    response = dynamodb.scan(TableName=DYNAMO_TABLE)
    for item in response['Items']:
        connectionid = item['connectionid']['S']
        url = item['url']['S']
        logger.debug(f'send_message_to_client "{connectionid}" message {message}')
        apigw = boto3.client('apigatewaymanagementapi', endpoint_url=url)
        try:
            apigw.post_to_connection(
                ConnectionId=connectionid,
                Data=message
            )
        except apigw.exceptions.GoneException:
            logger.error(f'Connection "{connectionid}" is no longer valid.')
        except Exception as e:
            logger.error(f'Error sending "{message}" to connection "{connectionid}" {str(e)}')


load_dotenv()
logger = logging.getLogger()
logger.setLevel(os.getenv('LOG_LEVEL'))

API_KEY = os.getenv('API_KEY')
AWS_REGION = os.getenv('REGION')
AIRPORT = os.getenv('AIRPORT')
DYNAMO_TABLE = os.getenv('DYNAMO_TABLE')
QUEUE_NAME = os.getenv('QUEUE_NAME')

CENTER = os.getenv('CENTER').split(':')
TOP_LEFT = os.getenv('TOP_LEFT').split(':')
BOTTOM_RIGHT = os.getenv('BOTTOM_RIGHT').split(':')
RADIUS = 30000

ACCOUNT_ID = boto3.client('sts').get_caller_identity().get('Account')

sqs = boto3.client('sqs', region_name=AWS_REGION)

fr_api = FlightRadar24API()
airport = fr_api.get_airport_details(AIRPORT)
position = airport['airport']['pluginData']['details']['position']
CENTER = [position['latitude'], position['longitude']]
bounds = fr_api.get_bounds_by_point(float(CENTER[0]), float(CENTER[1]), RADIUS)
b = bounds.split(',')
TOP_LEFT = [b[0], b[2]]
BOTTOM_RIGHT = [b[1], b[3]]
reset()
for i in range(1, 1000):
    list = {}
    for f in fr_api.get_flights(bounds=bounds):
        if f.origin_airport_iata == AIRPORT or f.destination_airport_iata == AIRPORT:
            list[f.registration] = {
                "position": [f.latitude, f.longitude],
                "code": f.aircraft_code,
                "origin": f.origin_airport_iata,
                "destination": f.destination_airport_iata,
                "number": f.number,
                "flying": (f.on_ground == 0),
                "airline": f.airline_iata,
                "altitude": int(f.altitude * 0.3048)
            }

    encoded_data = json.dumps(list)

    queue_url = f'https://sqs.{AWS_REGION}.amazonaws.com/{ACCOUNT_ID}/{QUEUE_NAME}'
    response = sqs.send_message(
        QueueUrl=queue_url,
        DelaySeconds=10,
        MessageBody=encoded_data
    )
    print(f"Sent event {i}")
    time.sleep(5)
