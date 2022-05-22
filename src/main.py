import boto3

dynamodb_client = boto3.resource('dynamodb')

try:
    response = dynamodb_client.create_table(
        AttributeDefinitions=[
            {
                'AttributeName': 'Artist',
                'AttributeType': 'S',
            }
        ],
        KeySchema=[
            {
                'AttributeName': 'Artist',
                'KeyType': 'HASH',
            }
        ],
        TableName='instance-email-mapping',
    )

except dynamodb_client.exceptions.ResourceInUseException:
    # do something here as you require
    pass
