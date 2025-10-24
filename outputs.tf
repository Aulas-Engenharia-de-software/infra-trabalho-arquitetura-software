output "urls_endpoints_api" {
  description = "URLs completas dos endpoints da API"
  value = {
    enviar_mensagem     = "${aws_api_gateway_stage.api_stage_prod.invoke_url}/enviar-mensagem"
    consultar_info_fila = "${aws_api_gateway_stage.api_stage_prod.invoke_url}/consultar-info-fila"
  }
}

output "sns_topic_arn" {
  description = "ARN do tópico SNS para entregas finais (Confirme a assinatura do e-mail!)"
  value       = aws_sns_topic.topico_entrega_final.arn
}

output "nomes_filas_criadas" {
  description = "Nomes das filas SQS principais criadas para os alunos"
  value       = [for queue in aws_sqs_queue.aluno_fila_principal : queue.name]
}


resource "aws_api_gateway_documentation_version" "doc_v1" {
  rest_api_id = aws_api_gateway_rest_api.api_atividades.id
  version     = "v1.0.0"
  description = "Versão inicial da API com modelos de dados"

  depends_on = [
    aws_api_gateway_documentation_part.doc_method_enviar_post,
    aws_api_gateway_documentation_part.doc_method_consulta_get,
    aws_api_gateway_documentation_part.doc_param_consulta_queueName
  ]
}

output "url_documentacao_api" {
  description = "URL para exportar a documentação OpenAPI 3.0"
  value       = "https://${aws_api_gateway_rest_api.api_atividades.id}.execute-api.${data.aws_region.current.name}.amazonaws.com/${aws_api_gateway_stage.api_stage_prod.stage_name}/swagger.json"
}

output "url_console_documentacao" {
  description = "Link para o console do API Gateway para visualizar e exportar a documentação"
  value       = "https://console.aws.amazon.com/apigateway/home?region=${data.aws_region.current.name}#/apis/${aws_api_gateway_rest_api.api_atividades.id}/stages/${aws_api_gateway_stage.api_stage_prod.stage_name}/documentation"
}