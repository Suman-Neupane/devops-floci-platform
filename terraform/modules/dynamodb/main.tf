variable "table_name" {
  type        = string
  description = "Name of the DynamoDB table"
}

variable "environment" {
  type        = string
  description = "Deployment environment"
}

resource "aws_dynamodb_table" "documents_metadata" {
  name         = var.table_name
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "document_id"

  attribute {
    name = "document_id"
    type = "S"
  }

  tags = {
    Name        = var.table_name
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}

output "table_name" {
  value = aws_dynamodb_table.documents_metadata.name
}

output "table_arn" {
  value = aws_dynamodb_table.documents_metadata.arn
}
