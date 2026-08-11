variable "queue_name" {
  type        = string
  description = "Name of the SQS queue"
}

variable "environment" {
  type        = string
  description = "Deployment environment"
}

resource "aws_sqs_queue" "document_events" {
  name                      = var.queue_name
  delay_seconds             = 0
  max_message_size          = 262144
  message_retention_seconds = 86400
  receive_wait_time_seconds = 10

  tags = {
    Name        = var.queue_name
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}

output "queue_url" {
  value = aws_sqs_queue.document_events.url
}

output "queue_arn" {
  value = aws_sqs_queue.document_events.arn
}
