import json
import boto3
import os

sqs_client = boto3.client('sqs')

def lambda_handler(event, context):
    aws_account_id = context.invoked_function_arn.split(":")[4]

    queue_name = None
    if event.get('queryStringParameters'):
        queue_name = event['queryStringParameters'].get('queueName')

    if not queue_name:
        return {'statusCode': 400, 'body': json.dumps({'message': 'Parâmetro "queueName" é obrigatório.'})}

    try:
        response_get_url = sqs_client.get_queue_url(
            QueueName=queue_name,
            QueueOwnerAWSAccountId=aws_account_id
        )
        queue_url = response_get_url['QueueUrl']

        queue_attributes = sqs_client.get_queue_attributes(
            QueueUrl=queue_url,
            AttributeNames=['ApproximateNumberOfMessages', 'ApproximateNumberOfMessagesNotVisible']
        )
        attributes = queue_attributes.get('Attributes', {})

        response_body = {
            "queueName": queue_name,
            "quantidadeMensagensVisiveis": int(attributes.get('ApproximateNumberOfMessages', 0)),
            "quantidadeMensagensEmTransito": int(attributes.get('ApproximateNumberOfMessagesNotVisible', 0))
        }
        return {'statusCode': 200, 'body': json.dumps(response_body)}

    except sqs_client.exceptions.QueueDoesNotExist:
        return {'statusCode': 404, 'body': json.dumps({'message': f'Fila SQS "{queue_name}" não encontrada.'})}
    except Exception as e:
        print(f"Erro: {e}")
        return {'statusCode': 500, 'body': json.dumps({'message': 'Erro interno ao consultar atributos.'})}