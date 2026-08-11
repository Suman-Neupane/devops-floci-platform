variable "environment" {
  type        = string
  default     = "local"
  description = "Target deployment environment (local, dev, prod)"
}

variable "bucket_name" {
  type        = string
  default     = "user-documents-bucket"
  description = "S3 bucket name for document uploads"
}

variable "dynamodb_table_name" {
  type        = string
  default     = "document-metadata"
  description = "DynamoDB table name for storing file metadata"
}

variable "sqs_queue_name" {
  type        = string
  default     = "document-processing-events"
  description = "SQS queue name for document event processing"
}
