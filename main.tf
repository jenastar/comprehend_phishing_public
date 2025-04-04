terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

# AWS provider configuration
# Uses the region defined in variables.tf
provider "aws" {
  region = var.region
}

# Get the current AWS account identity for resource naming
data "aws_caller_identity" "current" {} 