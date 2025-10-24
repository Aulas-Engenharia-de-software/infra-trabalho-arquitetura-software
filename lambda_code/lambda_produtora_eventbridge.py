import json
import boto3
import os
import random

events_client = boto3.client('events')
dynamodb_client = boto3.client('dynamodb')

def get_campos_faltando(body):
    campos_obrigatorios = ['nomeAluno', 'disciplina', 'recomendacaoSerie', 'fraseMotivacionalDia', 'notaQueMereco', 'nomeFila', 'entregaFinal']
    return [campo for campo in campos_obrigatorios if campo not in body]

def lambda_handler(event, context):
    event_bus_name = os.environ.get('EVENT_BUS_NAME')
    dynamo_table_name = os.environ.get('DYNAMO_TABLE_NAME')
    aws_account_id = context.invoked_function_arn.split(":")[4]
    aws_region = os.environ['REGION']

    try:
        body = json.loads(event.get('body', '{}'))
        campos_faltando = get_campos_faltando(body)
        if campos_faltando:
            return {'statusCode': 400, 'body': json.dumps({'message': 'Erro de validação.', 'campos_faltando': campos_faltando})}

        queue_name = body['nomeFila']
        queue_url = f"https://sqs.{aws_region}.amazonaws.com/{aws_account_id}/{queue_name}"
        body['queueUrl'] = queue_url

        evento_para_publicar = {
            'Source': 'fag.arquitetura.software',
            'DetailType': 'Atividade Recebida',
            'Detail': body,
            'EventBusName': event_bus_name
        }

        events_client.put_events(Entries=[evento_para_publicar])

        response_dynamo = dynamodb_client.scan(TableName=dynamo_table_name, Limit=100)
        frases = [item['frase']['S'] for item in response_dynamo.get('Items', [])]
        frase_aleatoria = random.choice(frases) if frases else "Recebido com sucesso."

        return {'statusCode': 200, 'body': json.dumps({'message': frase_aleatoria})}

    except Exception as e:
        print(f"Ocorreu um erro: {e}")
        return {'statusCode': 500, 'body': json.dumps({'message': 'Não foi possível processar sua mensagem.'})}