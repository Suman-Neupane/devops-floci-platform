module "s3_bucket" {
  source      = "./modules/s3"
  bucket_name = var.bucket_name
  environment = var.environment
}

module "dynamodb_table" {
  source      = "./modules/dynamodb"
  table_name  = var.dynamodb_table_name
  environment = var.environment
}

module "sqs_queue" {
  source      = "./modules/sqs"
  queue_name  = var.sqs_queue_name
  environment = var.environment
}
