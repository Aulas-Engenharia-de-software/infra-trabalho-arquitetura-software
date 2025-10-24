############################################## LAMBDA PRODUTORA ##############################################
data "archive_file" "lambda_produtora_zip" {
  type        = "zip"
  source_file = "${path.module}/lambda_code/lambda_produtora_eventbridge.py"
  output_path = "${path.module}/.terraform/lambda_produtora.zip"
}

resource "aws_lambda_function" "lambda_produtora" {
  filename         = data.archive_file.lambda_produtora_zip.output_path
  source_code_hash = data.archive_file.lambda_produtora_zip.output_base64sha256

  function_name = "lambda_produtora_eventbridge"
  role          = aws_iam_role.role_lambda_produtora.arn
  handler       = "lambda_produtora_eventbridge.lambda_handler"
  runtime       = "python3.11"

  environment {
    variables = {
      EVENT_BUS_NAME    = var.event_bus_name
      DYNAMO_TABLE_NAME = var.dynamo_table_name
      REGION            = var.aws_region
    }
  }

  depends_on = [
    aws_iam_role_policy.policy_lambda_produtora,
    data.archive_file.lambda_produtora_zip
  ]
}

############################################## LAMBDA ROTEADORA ##############################################
data "archive_file" "lambda_roteadora_zip" {
  type        = "zip"
  source_file = "${path.module}/lambda_code/lambda_roteadora_eventos_sqs.py"
  output_path = "${path.module}/.terraform/lambda_roteadora.zip"
}

resource "aws_lambda_function" "lambda_roteadora" {
  filename         = data.archive_file.lambda_roteadora_zip.output_path
  source_code_hash = data.archive_file.lambda_roteadora_zip.output_base64sha256

  function_name = "lambda_roteadora_eventos_sqs"
  role          = aws_iam_role.role_lambda_roteadora.arn
  handler       = "lambda_roteadora_eventos_sqs.lambda_handler"
  runtime       = "python3.11"

  depends_on = [
    aws_iam_role_policy.policy_lambda_roteadora,
    data.archive_file.lambda_roteadora_zip
  ]
}


############################################## LAMBDA CONSULTA ##############################################
data "archive_file" "lambda_consulta_zip" {
  type        = "zip"
  source_file = "${path.module}/lambda_code/lambda_consulta_filas.py"
  output_path = "${path.module}/.terraform/lambda_consulta.zip"
}

resource "aws_lambda_function" "lambda_consulta" {
  filename         = data.archive_file.lambda_consulta_zip.output_path
  source_code_hash = data.archive_file.lambda_consulta_zip.output_base64sha256

  function_name = "lambda_consulta_filas"
  role          = aws_iam_role.role_lambda_consulta.arn
  handler       = "lambda_consulta_filas.lambda_handler"
  runtime       = "python3.11"

  depends_on = [
    aws_iam_role_policy.policy_lambda_consulta,
    data.archive_file.lambda_consulta_zip
  ]
}