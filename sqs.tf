locals {
  student_names = toset([
    for s in split("\n", file("${path.module}/lista_alunos.txt")) : trimspace(s) if s != ""
  ])
}

resource "aws_sqs_queue" "aluno_dlq" {
  for_each = local.student_names

  name = "dlq_sqs_${each.key}"
}

resource "aws_sqs_queue" "aluno_fila_principal" {
  for_each = local.student_names

  name = "sqs_${each.key}"

  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.aluno_dlq[each.key].arn
    maxReceiveCount     = 5
  })
  visibility_timeout_seconds = 60
}