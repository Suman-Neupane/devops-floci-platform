terraform {
  required_version = ">= 1.5.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

variable "floci_endpoint" {
  type        = string
  default     = "http://localhost:4566"
  description = "Local Floci AWS emulator endpoint URL"
}

variable "aws_region" {
  type        = string
  default     = "eu-central-1"
  description = "AWS region for deployment"
}

provider "aws" {
  region                      = var.aws_region
  access_key                  = "mock_access_key"
  secret_key                  = "mock_secret_key"
  skip_credentials_validation = true
  skip_metadata_api_check     = true
  skip_requesting_account_id  = true
  s3_use_path_style           = true

  endpoints {
    s3       = var.floci_endpoint
    dynamodb = var.floci_endpoint
    sqs      = var.floci_endpoint
    iam      = var.floci_endpoint
    sts      = var.floci_endpoint
  }
}
