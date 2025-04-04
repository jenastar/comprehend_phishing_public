variable "region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "dev"
}

variable "model_name" {
  description = "Name of the Comprehend model"
  type        = string
  default     = "phishing-detection-model"
}

variable "endpoint_name" {
  description = "Name of the Comprehend endpoint"
  type        = string
  default     = "phishing-detection-endpoint"
}

variable "app_id" {
  description = "Application ID for tagging resources"
  type        = string
  default     = "YOUR_APP_ID"
} 