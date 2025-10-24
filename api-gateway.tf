resource "aws_api_gateway_rest_api" "api_atividades" {
  name        = "ApiAtividadesAlunos"
  description = "API para receber e consultar atividades dos alunos"
}

resource "aws_api_gateway_resource" "resource_enviar" {
  rest_api_id = aws_api_gateway_rest_api.api_atividades.id
  parent_id   = aws_api_gateway_rest_api.api_atividades.root_resource_id
  path_part   = "enviar-mensagem"
}

resource "aws_api_gateway_method" "method_enviar_post" {
  rest_api_id   = aws_api_gateway_rest_api.api_atividades.id
  resource_id   = aws_api_gateway_resource.resource_enviar.id
  http_method   = "POST"
  authorization = "NONE"

  request_validator_id = aws_api_gateway_request_validator.validate_body.id
  request_models = {
    "application/json" = aws_api_gateway_model.model_enviar_mensagem_request.name
  }
}

resource "aws_api_gateway_method_response" "enviar_response_200" {
  rest_api_id = aws_api_gateway_rest_api.api_atividades.id
  resource_id = aws_api_gateway_resource.resource_enviar.id
  http_method = aws_api_gateway_method.method_enviar_post.http_method
  status_code = "200"
  response_models = {
    "application/json" = aws_api_gateway_model.model_success_response.name
  }
}
resource "aws_api_gateway_method_response" "enviar_response_400" {
  rest_api_id = aws_api_gateway_rest_api.api_atividades.id
  resource_id = aws_api_gateway_resource.resource_enviar.id
  http_method = aws_api_gateway_method.method_enviar_post.http_method
  status_code = "400"
  response_models = {
    "application/json" = aws_api_gateway_model.model_error_response.name
  }
}

resource "aws_api_gateway_integration" "integration_enviar_lambda" {
  rest_api_id = aws_api_gateway_rest_api.api_atividades.id
  resource_id = aws_api_gateway_resource.resource_enviar.id
  http_method = aws_api_gateway_method.method_enviar_post.http_method

  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.lambda_produtora.invoke_arn
}

resource "aws_api_gateway_resource" "resource_consulta" {
  rest_api_id = aws_api_gateway_rest_api.api_atividades.id
  parent_id   = aws_api_gateway_rest_api.api_atividades.root_resource_id
  path_part   = "consultar-info-fila"
}

resource "aws_api_gateway_method" "method_consulta_get" {
  rest_api_id   = aws_api_gateway_rest_api.api_atividades.id
  resource_id   = aws_api_gateway_resource.resource_consulta.id
  http_method   = "GET"
  authorization = "NONE"

  request_parameters = {
    "method.request.querystring.queueName" = true
  }

  request_validator_id = aws_api_gateway_request_validator.validate_params.id
}

# Define as respostas possíveis para /consultar-info-fila
resource "aws_api_gateway_method_response" "consulta_response_200" {
  rest_api_id = aws_api_gateway_rest_api.api_atividades.id
  resource_id = aws_api_gateway_resource.resource_consulta.id
  http_method = aws_api_gateway_method.method_consulta_get.http_method
  status_code = "200"
  response_models = {
    "application/json" = aws_api_gateway_model.model_consulta_response.name
  }
}
resource "aws_api_gateway_method_response" "consulta_response_404" {
  rest_api_id = aws_api_gateway_rest_api.api_atividades.id
  resource_id = aws_api_gateway_resource.resource_consulta.id
  http_method = aws_api_gateway_method.method_consulta_get.http_method
  status_code = "404"
  response_models = {
    "application/json" = aws_api_gateway_model.model_error_response.name
  }
}

resource "aws_api_gateway_integration" "integration_consulta_lambda" {
  rest_api_id = aws_api_gateway_rest_api.api_atividades.id
  resource_id = aws_api_gateway_resource.resource_consulta.id
  http_method = aws_api_gateway_method.method_consulta_get.http_method

  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.lambda_consulta.invoke_arn
}

resource "aws_api_gateway_deployment" "api_deploy" {
  rest_api_id = aws_api_gateway_rest_api.api_atividades.id

  depends_on = [
    aws_api_gateway_integration.integration_enviar_lambda,
    aws_api_gateway_integration.integration_consulta_lambda,
    aws_api_gateway_method_response.enviar_response_200,
    aws_api_gateway_method_response.enviar_response_400,
    aws_api_gateway_method_response.consulta_response_200,
    aws_api_gateway_method_response.consulta_response_404
  ]

  triggers = {
    redeployment = sha1(jsonencode([
      aws_api_gateway_resource.resource_enviar.id,
      aws_api_gateway_method.method_enviar_post.id,
      aws_api_gateway_integration.integration_enviar_lambda.id,
      aws_api_gateway_resource.resource_consulta.id,
      aws_api_gateway_method.method_consulta_get.id,
      aws_api_gateway_integration.integration_consulta_lambda.id,

      aws_api_gateway_model.model_enviar_mensagem_request.id,
      aws_api_gateway_model.model_success_response.id,
      aws_api_gateway_model.model_consulta_response.id,
      aws_api_gateway_model.model_error_response.id
    ]))
  }

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_api_gateway_stage" "api_stage_prod" {
  deployment_id = aws_api_gateway_deployment.api_deploy.id
  rest_api_id   = aws_api_gateway_rest_api.api_atividades.id
  stage_name    = "prod"
}

resource "aws_lambda_permission" "allow_apigw_produtora" {
  statement_id  = "AllowAPIGatewayInvokeProdutora"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.lambda_produtora.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn = "${aws_api_gateway_rest_api.api_atividades.execution_arn}/${aws_api_gateway_stage.api_stage_prod.stage_name}/*/*"
}

resource "aws_lambda_permission" "allow_apigw_consulta" {
  statement_id  = "AllowAPIGatewayInvokeConsulta"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.lambda_consulta.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn = "${aws_api_gateway_rest_api.api_atividades.execution_arn}/${aws_api_gateway_stage.api_stage_prod.stage_name}/*/*"
}