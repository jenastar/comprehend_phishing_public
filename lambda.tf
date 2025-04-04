######################
# Lambda Functions
######################

# Endpoint Manager Lambda
resource "aws_lambda_function" "endpoint_manager" {
  filename         = "lambda/phishing_endpoint_manager.zip"
  function_name    = "phishing-endpoint-manager"
  role             = aws_iam_role.lambda_role.arn
  handler          = "phishing_endpoint_manager.lambda_handler"
  runtime          = "python3.9"
  timeout          = 30
  source_code_hash = filebase64sha256("lambda/phishing_endpoint_manager.zip")
  memory_size      = 128

  environment {
    variables = {
      MODEL_ARN = aws_comprehend_document_classifier.phishing_detector.arn
    }
  }
  
  tags = {
    Name        = "Phishing Endpoint Manager"
    Environment = var.environment
    Project     = "Phishing Detection"
    Function    = "Endpoint Management"
    AppID       = var.app_id
  }
}

# Phishing Detector Lambda
resource "aws_lambda_function" "phishing_detector" {
  filename         = "lambda/phishing_detector.zip"
  function_name    = "phishing-detector"
  role             = aws_iam_role.lambda_role.arn
  handler          = "phishing_detector.lambda_handler"
  runtime          = "python3.9"
  timeout          = 30
  source_code_hash = filebase64sha256("lambda/phishing_detector.zip")
  memory_size      = 128

  environment {
    variables = {
      ENDPOINT_MANAGER_FUNCTION = aws_lambda_function.endpoint_manager.function_name
    }
  }
  
  tags = {
    Name        = "Phishing Detector API"
    Environment = var.environment
    Project     = "Phishing Detection"
    Function    = "Text Classification"
    AppID       = var.app_id
  }
}

# Endpoint Cleanup Lambda
resource "aws_lambda_function" "endpoint_cleanup" {
  filename         = "lambda/phishing_endpoint_cleanup.zip"
  function_name    = "phishing-endpoint-cleanup"
  role             = aws_iam_role.lambda_role.arn
  handler          = "phishing_endpoint_cleanup.lambda_handler"
  runtime          = "python3.9"
  timeout          = 60
  memory_size      = 128
  source_code_hash = filebase64sha256("lambda/phishing_endpoint_cleanup.zip")
  
  tags = {
    Name        = "Phishing Endpoint Cleanup"
    Environment = var.environment
    Project     = "Phishing Detection"
    Function    = "Endpoint Cleanup"
    AppID       = var.app_id
  }
} 