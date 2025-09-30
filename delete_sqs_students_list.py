import boto3
from os import environ as env

AWS_REGION = env['AWS_REGION']
STUDENTS_FILE = env['STUDENTS_FILE']

iam_client = boto3.client('iam', region_name=AWS_REGION)
sqs_client = boto3.client('sqs', region_name=AWS_REGION)
sts_client = boto3.client('sts', region_name=AWS_REGION)


def open_students_file() -> list[str] | None:
    try:
        with open(STUDENTS_FILE, 'r') as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"ERRO: Arquivo '{STUDENTS_FILE}' não encontrado.")
        return None

def delete_sqs_for_students_list():
    students: list[str] = open_students_file()
    if students is None:
        print("Nenhum aluno encontrado.")
        return
    account_id = sts_client.get_caller_identity()['Account']

    for student_name in students:
        print(f"--- Desprovisionando para o aluno: {student_name} ---")

        user_name = f"aluno-{student_name}"
        policy_name = f"politica-sqs-{student_name}"
        policy_arn = f"arn:aws:iam::{account_id}:policy/{policy_name}"
        queue_name = f"fila-{student_name}"

        try:
            print(f"Deletando chaves de {user_name}...")
            for key in iam_client.list_access_keys(UserName=user_name)['AccessKeyMetadata']:
                iam_client.delete_access_key(UserName=user_name, AccessKeyId=key['AccessKeyId'])

            print(f"Desanexando e deletando política {policy_name}...")
            iam_client.detach_user_policy(UserName=user_name, PolicyArn=policy_arn)
            iam_client.delete_policy(PolicyArn=policy_arn)

            print(f"Deletando usuário {user_name}...")
            iam_client.delete_user(UserName=user_name)

        except Exception as e:
            print(
                f"Aviso: Não foi possível limpar recursos IAM para {user_name} (provavelmente já foram removidos). Erro: {e}")

        try:
            print(f"Deletando fila SQS {queue_name}...")
            queue_url = sqs_client.get_queue_url(QueueName=queue_name)['QueueUrl']
            sqs_client.delete_queue(QueueUrl=queue_url)
        except Exception as e:
            print(
                f"Aviso: Não foi possível deletar a fila SQS para {student_name} (provavelmente já foi removida). Erro: {e}")


if __name__ == "__main__":
    delete_sqs_for_students_list()
    input("Desprovisionamento concluído. Pressione [Enter] para sair.")