import boto3
import json
from os import environ as env

AWS_REGION = env.get('AWS_REGION', 'us-west-1')
AWS_ACCOUNT_ID = env.get('AWS_ACCOUNT_ID')
STUDENTS_FILE = env.get('STUDENTS_FILE')
MAX_RECEIVE_COUNT = 5

sqs_client = boto3.client('sqs', region_name=AWS_REGION)

def configurar_dlq_para_aluno(nome_aluno):
    nome_fila = f"fila_{nome_aluno}"
    nome_dlq = f"dlq_{nome_aluno}"

    print(f"--- Configurando DLQ para o aluno: {nome_aluno} ---")
    try:
        print(f"Procurando pela fila principal: {nome_fila}...")
        try:
            fila_principal_response = sqs_client.get_queue_url(
                QueueName=nome_fila,
                QueueOwnerAWSAccountId=AWS_ACCOUNT_ID
            )
            fila_principal_url = fila_principal_response['QueueUrl']
            print(f"Fila principal encontrada: {fila_principal_url}")
        except sqs_client.exceptions.QueueDoesNotExist:
            print(f"ERRO: A fila principal '{nome_fila}' não foi encontrada. Pulando este aluno.")
            return False

        print(f"Criando/Verificando DLQ: {nome_dlq}...")
        dlq_response = sqs_client.create_queue(QueueName=nome_dlq)
        dlq_url = dlq_response['QueueUrl']

        dlq_attributes = sqs_client.get_queue_attributes(
            QueueUrl=dlq_url,
            AttributeNames=['QueueArn']
        )
        dlq_arn = dlq_attributes['Attributes']['QueueArn']
        print(f"DLQ pronta com ARN: {dlq_arn}")

        print("Aplicando a Redrive Policy na fila principal...")
        redrive_policy = {
            "deadLetterTargetArn": dlq_arn,
            "maxReceiveCount": str(MAX_RECEIVE_COUNT)
        }

        sqs_client.set_queue_attributes(
            QueueUrl=fila_principal_url,
            Attributes={
                'RedrivePolicy': json.dumps(redrive_policy)
            }
        )

        print(f"Sucesso! A fila '{nome_fila}' agora usará '{nome_dlq}' como sua DLQ.")
        return True

    except Exception as e:
        print(f"ERRO inesperado ao configurar DLQ para {nome_aluno}: {e}")
        return False

def open_students_list_file() -> list[str] | None:
    try:
        with open(STUDENTS_FILE, 'r') as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"ERRO: Arquivo '{STUDENTS_FILE}' não encontrado.")
        return None

if __name__ == "__main__":
    alunos_sucesso = 0
    alunos_falha = 0

    print("Iniciando a atualização das filas existentes para usar DLQs...")
    students: list[str] = open_students_list_file()

    for aluno in students:
        if configurar_dlq_para_aluno(aluno):
            alunos_sucesso += 1
        else:
            alunos_falha += 1
        print("-" * 50)

    print("\nAtualização concluída.")
    print(f"  - {alunos_sucesso} filas configuradas com sucesso.")
    print(f"  - {alunos_falha} filas falharam ou foram puladas.")
