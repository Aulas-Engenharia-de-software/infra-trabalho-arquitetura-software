import boto3
import json
import sys
import time

AWS_REGION = "us-west-1"
USER_NAME = "consumidor_geral_alunos"
POLICY_NAME = "politica_consumo_filas_alunos"
DYNAMO_TABLE_NAME = "tb_eventos_recebidos"

iam_client = boto3.client('iam', region_name=AWS_REGION)
sts_client = boto3.client('sts', region_name=AWS_REGION)


def criar_ou_atualizar_usuario_e_politica():

    try:
        AWS_ACCOUNT_ID = sts_client.get_caller_identity()['Account']
        print(f"Configurando usuário IAM na conta: {AWS_ACCOUNT_ID}")

        SQS_RESOURCE_ARNS = [
            f"arn:aws:sqs:{AWS_REGION}:{AWS_ACCOUNT_ID}:sqs_*",
            f"arn:aws:sqs:{AWS_REGION}:{AWS_ACCOUNT_ID}:dlq_sqs_*"
        ]
        DYNAMO_TABLE_ARN = f"arn:aws:dynamodb:{AWS_REGION}:{AWS_ACCOUNT_ID}:table/{DYNAMO_TABLE_NAME}"

        print(f"Verificando/Criando usuário IAM: {USER_NAME}...")
        try:
            iam_client.create_user(UserName=USER_NAME)
            print("Usuário criado com sucesso.")
        except iam_client.exceptions.EntityAlreadyExistsException:
            print(f"Usuário '{USER_NAME}' já existe.")

        policy_document = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "PermissoesSQS",
                    "Effect": "Allow",
                    "Action": [
                        "sqs:ReceiveMessage",
                        "sqs:DeleteMessage",
                        "sqs:GetQueueAttributes",
                        "sqs:CreateQueue",
                        "sqs:SendMessage"
                    ],
                    "Resource": SQS_RESOURCE_ARNS
                },
                {
                    "Sid": "PermissoesDynamoDB",
                    "Effect": "Allow",
                    "Action": [
                        "dynamodb:PutItem"
                    ],
                    "Resource": DYNAMO_TABLE_ARN
                }
            ]
        }

        policy_arn = f"arn:aws:iam::{AWS_ACCOUNT_ID}:policy/{POLICY_NAME}"

        print(f"Tentando deletar a política antiga '{POLICY_NAME}' (se existir)...")
        try:
            entities = iam_client.list_entities_for_policy(PolicyArn=policy_arn)
            for user in entities.get('PolicyUsers', []):
                print(f" - Desanexando do usuário: {user['UserName']}")
                iam_client.detach_user_policy(UserName=user['UserName'], PolicyArn=policy_arn)

            iam_client.delete_policy(PolicyArn=policy_arn)
            print(f"Política antiga '{POLICY_NAME}' deletada.")
            time.sleep(5)
        except iam_client.exceptions.NoSuchEntityException:
            print(f"Política '{POLICY_NAME}' não encontrada, será criada.")
        except Exception as e:
            print(f"Aviso: Não foi possível deletar a política antiga. Erro: {e}", file=sys.stderr)
            print("Continuando para tentar criar a nova política...")

        print(f"Criando a nova política IAM: {POLICY_NAME}...")
        try:
            policy_response = iam_client.create_policy(
                PolicyName=POLICY_NAME,
                PolicyDocument=json.dumps(policy_document),
                Description="Permite acesso às filas SQS (incluindo envio), DLQs (envio) e escrita na tabela DynamoDB."
            )
            policy_arn = policy_response['Policy']['Arn']
            print(f"Nova política criada com sucesso: {policy_arn}")
            time.sleep(5)
        except iam_client.exceptions.EntityAlreadyExistsException:
            print(f"Erro: A política '{POLICY_NAME}' ainda existe. Tentando usar a existente.", file=sys.stderr)
            policy_arn = f"arn:aws:iam::{AWS_ACCOUNT_ID}:policy/{POLICY_NAME}"

        print(f"Anexando a nova política '{POLICY_NAME}' ao usuário '{USER_NAME}'...")
        try:
            iam_client.attach_user_policy(
                UserName=USER_NAME,
                PolicyArn=policy_arn
            )
            print("Política anexada com sucesso.")
        except Exception as e:
            print(f"Erro ao anexar a política '{policy_arn}' ao usuário '{USER_NAME}'. Erro: {e}", file=sys.stderr)
            raise e

        print("Criando novas chaves de acesso (Access Key)...")
        try:
            keys = iam_client.list_access_keys(UserName=USER_NAME)['AccessKeyMetadata']
            for key in keys:
                print(f"Removendo chave de acesso antiga: {key['AccessKeyId']}")
                iam_client.delete_access_key(UserName=USER_NAME, AccessKeyId=key['AccessKeyId'])
        except Exception as e:
            print(f"Aviso: Não foi possível remover chaves antigas. {e}", file=sys.stderr)

        key_response = iam_client.create_access_key(UserName=USER_NAME)
        access_key_id = key_response['AccessKey']['AccessKeyId']
        secret_access_key = key_response['AccessKey']['SecretAccessKey']

        print("\n" + "=" * 70)
        print(" SUCESSO! Usuário configurado e política ATUALIZADA (com SendMessage).")
        print(" Estas são as NOVAS credenciais para COMPARTILHAR com TODOS os alunos:")
        print("=" * 70)
        print(f"spring.cloud.aws.credentials.access-key={access_key_id}")
        print(f"spring.cloud.aws.credentials.secret-key={secret_access_key}")
        print("=" * 70 + "\n")

    except Exception as e:
        print(f"ERRO GERAL no processo: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    criar_ou_atualizar_usuario_e_politica()