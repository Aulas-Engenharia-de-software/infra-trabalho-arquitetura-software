resource "aws_sns_topic" "topico_entrega_final" {
  name = var.sns_topic_name
}

resource "aws_sns_topic_subscription" "email_subscription" {
  topic_arn = aws_sns_topic.topico_entrega_final.arn
  protocol  = "email"
  endpoint  = var.notification_email
}

resource "aws_sns_topic_policy" "sns_policy_eventbridge" {
  arn = aws_sns_topic.topico_entrega_final.arn
  policy = data.aws_iam_policy_document.sns_policy_eventbridge.json
}

data "aws_iam_policy_document" "sns_policy_eventbridge" {
  statement {
    effect = "Allow"
    principals {
      type        = "Service"
      identifiers = ["events.amazonaws.com"]
    }
    actions   = ["sns:Publish"]
    resources = [aws_sns_topic.topico_entrega_final.arn]
    condition {
      test     = "ArnLike"
      variable = "AWS:SourceArn"
      values   = [aws_cloudwatch_event_rule.regra_trabalho_final.arn]
    }
  }
}