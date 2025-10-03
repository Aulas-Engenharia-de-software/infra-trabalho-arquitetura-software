import json
import time
from os import environ as env

import boto3

AWS_REGION = env.get('AWS_REGION', 'us-west-1')
OUTPUT_FILE = env.get('OUTPUT_FILE', 'arquivos/credenciais_alunos.txt')
STUDENTS_FILE = env.get('STUDENTS_FILE', 'arquivos/alunos.txt')
PREFIX_SQS = env.get('PREFIX_SQS', 'fila_')
PAUSE_TIME = 2

iam_client = boto3.client('iam', region_name=AWS_REGION)
sqs_client = boto3.client('sqs', region_name=AWS_REGION)
sts_client = boto3.client('sts', region_name=AWS_REGION)


def create_sqs_for_students_list():
    students: list[str] = open_students_list_file()
    if not students:
        print("Nenhum aluno encontrado ou arquivo não localizado.")
        return

    account_id = sts_client.get_caller_identity()['Account']

    with open(OUTPUT_FILE, 'w') as f:
        f.write("Arquivo de credenciais Geradas para os Alunos\n\n")

    for student_name in students:
        print(f"--- Processando para o aluno: {student_name} ---")

        queue_name = f"{PREFIX_SQS}{student_name}"
        user_name = f"aluno_{student_name}"
        policy_name = f"politica_sqs_{student_name}"
        policy_arn = f"arn:aws:iam::{account_id}:policy/{policy_name}"

        try:
            print(f"Criando fila SQS: {queue_name}...")
            response = sqs_client.create_queue(QueueName=queue_name)
            queue_url = response['QueueUrl']
            time.sleep(PAUSE_TIME)

            response = sqs_client.get_queue_attributes(QueueUrl=queue_url, AttributeNames=['QueueArn'])
            queue_arn = response['Attributes']['QueueArn']

            create_user_iam(user_name)
            create_and_attach_user_policy(policy_arn, policy_name, queue_arn, user_name)

            print("Gerando chaves de acesso...")
            for key in iam_client.list_access_keys(UserName=user_name)['AccessKeyMetadata']:
                iam_client.delete_access_key(UserName=user_name, AccessKeyId=key['AccessKeyId'])

            key_response = iam_client.create_access_key(UserName=user_name)
            access_key_id = key_response['AccessKey']['AccessKeyId']
            secret_access_key = key_response['AccessKey']['SecretAccessKey']

            with open(OUTPUT_FILE, 'a') as f:
                f.write(f"--- Aluno: {student_name} ---\n")
                f.write(f"Queue URL: {queue_url}\n")
                f.write(f"Access Key ID: {access_key_id}\n")
                f.write(f"Secret Access Key: {secret_access_key}\n\n")
            print(f"Credenciais para {student_name} salvas com sucesso.")

        except Exception as e:
            print(f"ERRO ao processar {student_name}: {e}")


def open_students_list_file() -> list[str] | None:
    try:
        with open(STUDENTS_FILE, 'r') as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"ERRO: Arquivo '{STUDENTS_FILE}' não encontrado.")
        return None


def create_user_iam(user_name):
    print(f"Criando usuário IAM: {user_name}...")
    try:
        iam_client.create_user(UserName=user_name)
    except iam_client.exceptions.EntityAlreadyExistsException:
        print(f"Usuário {user_name} já existe.")


def create_and_attach_user_policy(policy_arn, policy_name, queue_arn, user_name):
    print(f"Criando e anexando política IAM: {policy_name}...")
    policy_document = {
        "Version": "2012-10-17",
        "Statement": [{
            "Effect": "Allow",
            "Action": ["sqs:ReceiveMessage", "sqs:DeleteMessage", "sqs:GetQueueAttributes"],
            "Resource": queue_arn
        }]
    }
    try:
        iam_client.create_policy(PolicyName=policy_name, PolicyDocument=json.dumps(policy_document))
    except iam_client.exceptions.EntityAlreadyExistsException:
        print(f"Política {policy_name} já existe.")

    iam_client.attach_user_policy(UserName=user_name, PolicyArn=policy_arn)


if __name__ == "__main__":
    create_sqs_for_students_list()
    input("Provisionamento concluído. Pressione [Enter] para sair.")