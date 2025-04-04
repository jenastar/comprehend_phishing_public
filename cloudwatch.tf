######################
# CloudWatch Events
######################

# CloudWatch Event Rule (runs every 5 minutes)
resource "aws_cloudwatch_event_rule" "cleanup_schedule" {
  name                = "phishing-endpoint-cleanup-schedule"
  description         = "Triggers the cleanup Lambda every 5 minutes to remove endpoints older than 5 minutes"
  schedule_expression = "rate(5 minutes)"
  
  tags = {
    Name        = "Phishing Cleanup Schedule"
    Environment = var.environment
    Project     = "Phishing Detection"
    AppID       = var.app_id
  }
}

# CloudWatch Event Target
resource "aws_cloudwatch_event_target" "cleanup_target" {
  rule      = aws_cloudwatch_event_rule.cleanup_schedule.name
  target_id = "phishing-endpoint-cleanup"
  arn       = aws_lambda_function.endpoint_cleanup.arn
} 