resource "aws_api_gateway_model" "model_enviar_mensagem_request" {
  rest_api_id  = aws_api_gateway_rest_api.api_atividades.id
  name         = "EnviarMensagemRequest"
  description  = "Corpo (body) JSON esperado para enviar uma atividade."
  content_type = "application/json"

  schema = jsonencode({
    type = "object",
    properties = {
      nomeAluno = { type = "string" },
      disciplina = { type = "string" },
      recomendacaoSerie = { type = "string" },
      fraseMotivacionalDia = { type = "string" },
      notaQueMereco = { type = "number" }, # Usando 'number' para notas
      nomeFila = { type = "string" },
      entregaFinal = { type = "boolean" }
    },
    required = [
      "nomeAluno",
      "disciplina",
      "recomendacaoSerie",
      "fraseMotivacionalDia",
      "notaQueMereco",
      "nomeFila",
      "entregaFinal"
    ]
  })
}

resource "aws_api_gateway_model" "model_success_response" {
  rest_api_id  = aws_api_gateway_rest_api.api_atividades.id
  name         = "SuccessResponse"
  description  = "Resposta genérica de sucesso com uma mensagem."
  content_type = "application/json"
  schema = jsonencode({
    type = "object",
    properties = {
      message = { type = "string" }
    }
  })
}

resource "aws_api_gateway_model" "model_consulta_response" {
  rest_api_id  = aws_api_gateway_rest_api.api_atividades.id
  name         = "ConsultaFilaResponse"
  description  = "Resposta da consulta de status da fila."
  content_type = "application/json"
  schema = jsonencode({
    type = "object",
    properties = {
      queueName = { type = "string" },
      quantidadeMensagensVisiveis = { type = "integer" },
      quantidadeMensagensEmTransito = { type = "integer" }
    }
  })
}

resource "aws_api_gateway_model" "model_error_response" {
  rest_api_id  = aws_api_gateway_rest_api.api_atividades.id
  name         = "ErrorResponse"
  description  = "Resposta de erro."
  content_type = "application/json"
  schema = jsonencode({
    type = "object",
    properties = {
      message = { type = "string" },
      # Opcional, para o erro de validação
      campos_faltando = {
        type = "array",
        items = { type = "string" }
      }
    }
  })
}

resource "aws_api_gateway_request_validator" "validate_body" {
  name                        = "ValidateRequestBody"
  rest_api_id                 = aws_api_gateway_rest_api.api_atividades.id
  validate_request_body = true
  validate_request_parameters = false
}

resource "aws_api_gateway_request_validator" "validate_params" {
  name                        = "ValidateRequestParameters"
  rest_api_id                 = aws_api_gateway_rest_api.api_atividades.id
  validate_request_body       = false
  validate_request_parameters = true
}



resource "aws_api_gateway_documentation_part" "doc_method_enviar_post" {
  rest_api_id = aws_api_gateway_rest_api.api_atividades.id
  location {
    type   = "METHOD"
    method = "POST"
    path   = "/enviar-mensagem"
  }
  properties = jsonencode({
    "summary" : "Enviar Atividade",
    "description" : "Recebe os dados de uma atividade, valida, e publica no barramento de eventos para processamento assíncrono."
  })
}

resource "aws_api_gateway_documentation_part" "doc_method_consulta_get" {
  rest_api_id = aws_api_gateway_rest_api.api_atividades.id
  location {
    type   = "METHOD"
    method = "GET"
    path   = "/consultar-info-fila"
  }
  properties = jsonencode({
    "summary" : "Consultar Status da Fila",
    "description" : "Consulta os atributos de uma fila SQS específica para ver a quantidade de mensagens visíveis e em trânsito."
  })
}

resource "aws_api_gateway_documentation_part" "doc_param_consulta_queueName" {
  rest_api_id = aws_api_gateway_rest_api.api_atividades.id
  location {
    type   = "QUERY_PARAMETER"
    method = "GET"
    path   = "/consultar-info-fila"
    name   = "queueName"
  }
  properties = jsonencode({
    "description" = "O nome exato da fila SQS a ser consultada (ex: sqs_alex_roberto_hoffmann). Este parâmetro é obrigatório."
  })
}