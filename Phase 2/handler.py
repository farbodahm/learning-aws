import json
import numpy as np
import boto3
import os
import base64
import gzip


def get_matrix_inverse(event, context):
    body = json.loads(event['body'])
    matrix = np.matrix(body['matrix'])
    matrix_inverse = matrix.I

    data = {"matrix": matrix.tolist(), "inverse_matrix": matrix_inverse.tolist()}
    data_dumped = json.dumps(data)

    # Log to CloudWatch
    print(data_dumped)

    sns_client = boto3.client('sns')
    SNS_ARN = os.getenv('SNS_ARN')
    response = sns_client.publish(
        TopicArn=SNS_ARN,
        Message=data_dumped,
        Subject='Inverse of Matrix'
    )

    result = {
        'statusCode': 200,
        'message': f"Inverse of the matrix is sent with id {response['MessageId']}",
        'data': data,
    }
    return json.dumps(result)


def preprocess(event, context):
    count = 0
    for record in event['Records']:
        event_id = record['eventID']
        # timestamp = record['kinesis']['approximateArrivalTimestamp']

        # Kinesis data is base64-encoded, so decode here
        data = base64.b64decode(record['kinesis']['data'])
        
        # Kinesis data is Gzip-compressed, so decompress here
        message = json.loads(gzip.decompress(data).decode('utf-8'))
        
        print(message)
        
        records = []
        for log_event in message['logEvents']:
            log = {}
            log['data'] = json.loads(log_event['message'])
            log['timestamp'] = log_event['timestamp']
            log['event_id'] = event_id
            
            log = json.dumps(log)
            log += "\n"
            
            records.append({
                'Data': log.encode('utf-8')
            })

        print(records)
        client = boto3.client('firehose')
        response = client.put_record_batch(
            DeliveryStreamName='farbod-matrix-inverse',
            Records=records
        )
        
        print(response)
        # Index the document
        count += 1

    print('Processed ' + str(count) + ' event records.')
 
    return {
        'statusCode': 200,
        'processed': count
    }
