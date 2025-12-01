import boto3
import json
import logging
import os
import base64

REGION = os.getenv('REGION')
DYNAMO_TABLE = os.getenv('DYNAMO_TABLE')

logger = logging.getLogger()
logger.setLevel(os.getenv('LOG_LEVEL'))


def lambda_handler(event, context):
    logger.debug(f'event {json.dumps(event, indent=2)}')
    for record in event['Records']:
        try:
            message = json.dumps({
                'type': 'show',
                'aircrafts': json.loads(record['body'])
            })
            dynamodb = boto3.client('dynamodb', region_name=REGION)
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
        except Exception as e:
            logger.error(f'Error reading records {str(e)}')
