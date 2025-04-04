output "model_arn" {
  value = aws_comprehend_document_classifier.phishing_detector.arn
  description = "ARN of the Comprehend model"
}

output "s3_bucket_arn" {
  value = aws_s3_bucket.phishing_detection.arn
  description = "ARN of the S3 bucket"
}

output "iam_role_arn" {
  value = aws_iam_role.comprehend_role.arn
  description = "ARN of the IAM role"
}

output "api_gateway_url" {
  value = "${aws_apigatewayv2_stage.phishing_stage.invoke_url}/detect"
  description = "URL of the API Gateway endpoint"
} 