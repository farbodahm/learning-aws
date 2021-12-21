import json
import numpy as np
import boto3
import os


def hello(event, context):
    body = json.loads(event['body'])
    matrix = np.matrix(body['matrix'])
    msg = f'Given matrix:\n{str(matrix)}\nInverse of matrix:\n{str(matrix.I)}'

    sns_client = boto3.client('sns')
    SNS_ARN = os.getenv('SNS_ARN')
    response = sns_client.publish(
        TopicArn=SNS_ARN,
        Message=msg,
        Subject='Inverse of Matrix'
    )

    result = {
        'statusCode': 200,
        'message': f"Inverse of the matrix is sent with id {response['MessageId']}",
    }
    return json.dumps(result)
