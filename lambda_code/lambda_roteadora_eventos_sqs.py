import json
import boto3

sqs_client = boto3.client('sqs')

def lambda_handler(event, context):
    print(f"Evento recebido: {event}")
    try:
        detalhe_evento = event['detail']
        url_fila_aluno = detalhe_evento['queueUrl']

        sqs_client.send_message(
            QueueUrl=url_fila_aluno,
            MessageBody=json.dumps(detalhe_evento)
        )

        print(f"Mensagem encaminhada com sucesso para a fila: {url_fila_aluno}")
        return {
            'statusCode': 200,
            'body': json.dumps('Mensagem roteada com sucesso!')
        }

    except KeyError as e:
        print(f"ERRO: Chave esperada não encontrada no evento. Chave faltante: {e}")
        raise e
    except Exception as e:
        print(f"ERRO inesperado ao processar o evento: {e}")
        raise e