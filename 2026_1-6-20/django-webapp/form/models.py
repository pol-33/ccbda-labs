import boto3
from django.conf import settings
import logging

logger = logging.getLogger('django')


class Leads():

    def insert_lead(self, name, email, previewAccess):
        try:
            dynamodb = boto3.resource('dynamodb',
                                      region_name=settings.AWS_REGION,
                                      aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                                      aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                                      aws_session_token=settings.AWS_SESSION_TOKEN)
            table = dynamodb.Table(settings.CCBDA_SIGNUP_TABLE)
        except Exception as e:
            logger.error(
                'Error connecting to database table: ' + (e.fmt if hasattr(e, 'fmt') else '') + ','.join(e.args))
            return 403
        try:
            response = table.put_item(
                Item={
                    'name': name,
                    'email': email,
                    'preview': previewAccess,
                },
                ReturnValues='ALL_OLD',
            )
        except Exception as e:
            logger.error(
                'Error adding item to database: ' + (e.fmt if hasattr(e, 'fmt') else '') + ','.join(e.args))
            return 403
        status = response['ResponseMetadata']['HTTPStatusCode']
        if status == 200:
            if 'Attributes' in response:
                logger.info('Existing item updated to database.')
                return 409
            logger.info('New item added to database.')
        else:
            logger.error('Unknown error inserting item to database.')

        return status
    
    def send_notification(self, email):
        sns = boto3.client('sns', region_name=settings.AWS_REGION,
                        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)
        try:
            sns.publish(
                TopicArn=settings.NEW_SIGNUP_TOPIC,
                Message='New signup: %s' % email,
                Subject='New signup',
            )
            logger.error('SNS message sent.')

        except Exception as e:
            logger.error(
                'Error sending AWS SNS message: ' + (e.fmt if hasattr(e, 'fmt') else '') + ','.join(e.args))

    def get_leads(self, domain, preview):
        try:
            dynamodb = boto3.resource('dynamodb',
                                      region_name=settings.AWS_REGION,
                                      aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                                      aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)
            table = dynamodb.Table('ccbda-signup-table')
        except Exception as e:
            logger.error(
                'Error connecting to database table: ' + (e.fmt if hasattr(e, 'fmt') else '') + ','.join(e.args))
            return None
        expression_attribute_values = {}
        FilterExpression = []
        if preview:
            expression_attribute_values[':p'] = preview
            FilterExpression.append('preview = :p')
        if domain:
            expression_attribute_values[':d'] = '@' + domain
            FilterExpression.append('contains(email, :d)')
        if expression_attribute_values and FilterExpression:
            response = table.scan(
                FilterExpression=' and '.join(FilterExpression),
                ExpressionAttributeValues=expression_attribute_values,
            )
        else:
            response = table.scan(
                ReturnConsumedCapacity='TOTAL',
            )
        if response['ResponseMetadata']['HTTPStatusCode'] == 200:
            return response['Items']
        logger.error('Unknown error retrieving items from database.')
        return None

