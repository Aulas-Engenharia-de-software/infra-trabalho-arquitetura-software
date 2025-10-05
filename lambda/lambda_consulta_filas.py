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
        return {
            'statusCode': 400,
            'body': json.dumps({'message': 'Parâmetro "queueName" é obrigatório.'})
        }

    try:
        response_get_url = sqs_client.get_queue_url(
            QueueName=queue_name,
            QueueOwnerAWSAccountId=aws_account_id
        )
        queue_url = response_get_url['QueueUrl']

        queue_attributes = sqs_client.get_queue_attributes(
            QueueUrl=queue_url,
            AttributeNames=['ApproximateNumberOfMessages']
        )
        message_count = int(queue_attributes.get('Attributes', {}).get('ApproximateNumberOfMessages', 0))

        response_receive = sqs_client.receive_message(
            QueueUrl=queue_url,
            MaxNumberOfMessages=10,
            VisibilityTimeout=0,
            MessageAttributeNames=['All']
        )

        messages = response_receive.get('Messages', [])

        formatted_messages = []
        seen_ids = []
        for msg in messages:
            body_content = msg.get('Body', '')
            try:
                body_content = json.loads(body_content)
            except json.JSONDecodeError:
                pass

            message_id = msg.get("MessageId")
            if message_id in seen_ids:
                continue

            seen_ids.append(message_id)
            formatted_messages.append({
                'messageId': message_id,
                'body': body_content
            })

        return {
            'statusCode': 200,
            'body': json.dumps({
                'quantidadeNensagensVisiveis': message_count,
                'mensagensNoLote': formatted_messages,
            })
        }

    except sqs_client.exceptions.QueueDoesNotExist:
        return {
            'statusCode': 404,
            'body': json.dumps({'message': f'Fila SQS "{queue_name}" não encontrada ou não pertence a esta conta.'})
        }
    except Exception as e:
        print(f"Erro ao consultar fila SQS: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({'message': 'Erro interno ao consultar a fila.'})
        }