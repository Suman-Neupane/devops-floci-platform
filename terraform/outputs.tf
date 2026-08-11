output "s3_bucket_name" {
  value       = module.s3_bucket.bucket_id
  description = "Name of the provisioned S3 bucket"
}

output "dynamodb_table_name" {
  value       = module.dynamodb_table.table_name
  description = "Name of the provisioned DynamoDB table"
}

output "sqs_queue_url" {
  value       = module.sqs_queue.queue_url
  description = "URL of the provisioned SQS queue"
}
