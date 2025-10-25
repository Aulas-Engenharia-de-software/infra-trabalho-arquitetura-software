resource "aws_dynamodb_table" "frases_api" {
  name         = var.dynamo_table_name
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "id"

  attribute {
    name = "id"
    type = "S"
  }

  tags = {
    Name      = var.dynamo_table_name
    Project   = "AtividadesAlunos"
    ManagedBy = "Terraform"
  }
}

resource "aws_dynamodb_table" "eventos_recebidos" {
  name = "tb_eventos_recebidos"
  billing_mode = "PAY_PER_REQUEST"
  hash_key = "id"

  attribute {
    name = "id"
    type = "S"
  }
  tags = {
    Name      = "tb_eventos_recebidos"
    Project   = "AtividadesAlunos"
    ManagedBy = "Terraform"
  }
}