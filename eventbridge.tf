resource "aws_cloudwatch_event_bus" "barramento_alunos" {
  name = var.event_bus_name
}

resource "aws_cloudwatch_event_rule" "regra_roteadora" {
  name           = "RoteiaAtividadeRecebidaParaLambda"
  event_bus_name = aws_cloudwatch_event_bus.barramento_alunos.name

  event_pattern = jsonencode({
    "source" : ["fag.arquitetura.software"],
    "detail-type" : ["Atividade Recebida"]
  })
}

resource "aws_cloudwatch_event_target" "target_lambda_roteadora" {
  rule           = aws_cloudwatch_event_rule.regra_roteadora.name
  event_bus_name = aws_cloudwatch_event_bus.barramento_alunos.name
  arn            = aws_lambda_function.lambda_roteadora.arn
}

resource "aws_lambda_permission" "allow_eventbridge_roteadora" {
  statement_id  = "AllowEventBridgeInvokeLambdaRoteadora"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.lambda_roteadora.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.regra_roteadora.arn
}

resource "aws_cloudwatch_event_rule" "regra_trabalho_final" {
  name           = "EncaminhaTrabalhoFinalParaSNS"
  event_bus_name = aws_cloudwatch_event_bus.barramento_alunos.name

  event_pattern = jsonencode({
    "source" : ["fag.arquitetura.software"],
    "detail-type" : ["Atividade Recebida"],
    "detail" : {
      "entregaFinal" : [true]
    }
  })
}

resource "aws_cloudwatch_event_target" "target_sns_trabalho_final" {
  rule           = aws_cloudwatch_event_rule.regra_trabalho_final.name
  event_bus_name = aws_cloudwatch_event_bus.barramento_alunos.name
  arn            = aws_sns_topic.topico_entrega_final.arn # Depende do SNS
}