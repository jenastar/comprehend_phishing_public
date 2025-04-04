######################
# API Gateway
######################

# API Gateway
resource "aws_apigatewayv2_api" "phishing_api" {
  name          = "phishing-detection-api"
  protocol_type = "HTTP"
  description   = "API for phishing email detection"
  
  tags = {
    Name        = "Phishing Detection API"
    Environment = var.environment
    Project     = "Phishing Detection"
    Function    = "API Gateway"
    AppID       = var.app_id
  }
}

# API Gateway stage
resource "aws_apigatewayv2_stage" "phishing_stage" {
  api_id = aws_apigatewayv2_api.phishing_api.id
  name   = "prod"
  auto_deploy = true
  
  tags = {
    Name        = "Phishing API Stage"
    Environment = var.environment
    Project     = "Phishing Detection"
    Function    = "API Gateway Stage"
    AppID       = var.app_id
  }
}

# API Gateway integration with Lambda
resource "aws_apigatewayv2_integration" "phishing_integration" {
  api_id           = aws_apigatewayv2_api.phishing_api.id
  integration_type = "AWS_PROXY"

  connection_type    = "INTERNET"
  description        = "Lambda integration"
  integration_method = "POST"
  integration_uri    = aws_lambda_function.phishing_detector.invoke_arn
}

# API Gateway route
resource "aws_apigatewayv2_route" "phishing_route" {
  api_id    = aws_apigatewayv2_api.phishing_api.id
  route_key = "POST /detect"
  target    = "integrations/${aws_apigatewayv2_integration.phishing_integration.id}"
} 