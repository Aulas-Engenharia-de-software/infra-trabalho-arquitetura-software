variable "aws_region" {
  description = "Região da AWS para implantar os recursos"
  type        = string
  default     = "us-west-1"
}

variable "event_bus_name" {
  description = "Nome do barramento de eventos principal"
  type        = string
  default     = "barramento_atividades_alunos"
}

variable "dynamo_table_name" {
  description = "Nome da tabela DynamoDB com as frases da API"
  type        = string
  default     = "tb_frases_api"
}

variable "sns_topic_name" {
  description = "Nome do tópico SNS para entregas finais"
  type        = string
  default     = "topico_entrega_final"
}

variable "notification_email" {
  description = "E-mail para receber notificações de entregas finais (deve ser confirmado!)"
  type        = string
  default     = "lucasmartins@fag.edu.br"
}