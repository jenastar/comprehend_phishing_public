######################
# Permissions
######################

# API Gateway Lambda Permission
resource "aws_lambda_permission" "api_gw" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.phishing_detector.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.phishing_api.execution_arn}/*/*"
}

# Endpoint Manager Lambda Permission
resource "aws_lambda_permission" "endpoint_manager_invoke" {
  statement_id  = "AllowInvocationFromAnalyzer"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.endpoint_manager.function_name
  principal     = "lambda.amazonaws.com"
  source_arn    = aws_lambda_function.phishing_detector.arn
}

# CloudWatch Event Lambda Permission
resource "aws_lambda_permission" "allow_cloudwatch" {
  statement_id  = "AllowExecutionFromCloudWatch"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.endpoint_cleanup.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.cleanup_schedule.arn
} 