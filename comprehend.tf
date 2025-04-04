######################
# Comprehend Resources
######################

resource "aws_comprehend_document_classifier" "phishing_detector" {
  name         = var.model_name
  version_name = "v1-phishing-detector"
  data_access_role_arn = aws_iam_role.comprehend_role.arn
  language_code = "en"
  mode = "MULTI_CLASS"

  input_data_config {
    s3_uri = "s3://${aws_s3_bucket.phishing_detection.bucket}/training/"
  }

  output_data_config {
    s3_uri = "s3://${aws_s3_bucket.phishing_detection.bucket}/output/"
  }

  tags = {
    Name        = "Phishing Detection Model"
    Environment = var.environment
    Project     = "Phishing Detection"
    AppID       = var.app_id
  }
}

