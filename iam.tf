data "aws_iam_policy_document" "assume_role_lambda" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
  }
}


############################################## LAMBDA PRODUTORA ##############################################
resource "aws_iam_role" "role_lambda_produtora" {
  name               = "role_lambda_produtora"
  assume_role_policy = data.aws_iam_policy_document.assume_role_lambda.json
}

data "aws_iam_policy_document" "policy_lambda_produtora" {
  statement {
    effect = "Allow"
    actions = [
      "logs:CreateLogGroup",
      "logs:CreateLogStream",
      "logs:PutLogEvents"
    ]
    resources = ["arn:aws:logs:*:*:*"]
  }

  statement {
    effect = "Allow"
    actions = ["events:PutEvents"]
    resources = [
      "arn:aws:events:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:event-bus/${var.event_bus_name}"
    ]
  }

  statement {
    effect = "Allow"
    actions = ["dynamodb:Scan"]
    resources = [
      "arn:aws:dynamodb:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:table/${var.dynamo_table_name}"
    ]
  }
}

resource "aws_iam_role_policy" "policy_lambda_produtora" {
  name   = "politica_lambda_produtora"
  role   = aws_iam_role.role_lambda_produtora.id
  policy = data.aws_iam_policy_document.policy_lambda_produtora.json
}


############################################## LAMBDA ROTEADORA ##############################################
resource "aws_iam_role" "role_lambda_roteadora" {
  name               = "role_lambda_roteadora"
  assume_role_policy = data.aws_iam_policy_document.assume_role_lambda.json
}

data "aws_iam_policy_document" "policy_lambda_roteadora" {
  statement {
    effect = "Allow"
    actions = [
      "logs:CreateLogGroup",
      "logs:CreateLogStream",
      "logs:PutLogEvents"
    ]
    resources = ["arn:aws:logs:*:*:*"]
  }

  statement {
    effect = "Allow"
    actions = ["sqs:SendMessage"]
    resources = ["arn:aws:sqs:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:sqs_*"]
  }
}

resource "aws_iam_role_policy" "policy_lambda_roteadora" {
  name   = "politica_lambda_roteadora"
  role   = aws_iam_role.role_lambda_roteadora.id
  policy = data.aws_iam_policy_document.policy_lambda_roteadora.json
}


############################################## LAMBDA CONSULTA ##############################################
resource "aws_iam_role" "role_lambda_consulta" {
  name               = "role_lambda_consulta"
  assume_role_policy = data.aws_iam_policy_document.assume_role_lambda.json
}

data "aws_iam_policy_document" "policy_lambda_consulta" {
  statement {
    effect = "Allow"
    actions = [
      "logs:CreateLogGroup",
      "logs:CreateLogStream",
      "logs:PutLogEvents"
    ]
    resources = ["arn:aws:logs:*:*:*"]
  }
  statement {
    effect = "Allow"
    actions = [
      "sqs:GetQueueAttributes",
      "sqs:GetQueueUrl"
    ]
    resources = [
      "arn:aws:sqs:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:sqs_*",
      "arn:aws:sqs:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:dlq_sqs_*"
    ]
  }
  statement {
    effect = "Allow"
    actions = ["sqs:ListQueues"]
    resources = ["*"]
  }
}

resource "aws_iam_role_policy" "policy_lambda_consulta" {
  name   = "politica_lambda_consulta"
  role   = aws_iam_role.role_lambda_consulta.id
  policy = data.aws_iam_policy_document.policy_lambda_consulta.json
}