######################
# IAM Roles & Policies
######################

# IAM role for Lambda
resource "aws_iam_role" "lambda_role" {
  name = "phishing-detector-lambda-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
  
  tags = {
    Name        = "Phishing Lambda Role"
    Environment = var.environment
    Project     = "Phishing Detection"
    AppID       = var.app_id
  }
}

# IAM policy for Lambda
resource "aws_iam_role_policy" "lambda_policy" {
  name = "phishing-detector-lambda-policy"
  role = aws_iam_role.lambda_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "comprehend:DetectEntities",
          "comprehend:DetectKeyPhrases",
          "comprehend:DetectSentiment",
          "comprehend:DetectSyntax",
          "comprehend:ClassifyDocument",
          "comprehend:CreateEndpoint",
          "comprehend:DescribeEndpoint",
          "comprehend:ListEndpoints",
          "comprehend:DeleteEndpoint"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "arn:aws:logs:*:*:*"
      },
      {
        Effect = "Allow"
        Action = [
          "lambda:InvokeFunction"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "sts:GetCallerIdentity"
        ]
        Resource = "*"
      }
    ]
  })
}

# IAM role for Comprehend
resource "aws_iam_role" "comprehend_role" {
  name = "phishing-detection-comprehend-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "comprehend.amazonaws.com"
        }
      }
    ]
  })
  
  tags = {
    Name        = "Phishing Comprehend Role"
    Environment = var.environment
    Project     = "Phishing Detection"
    AppID       = var.app_id
  }
}

# IAM policy for Comprehend
resource "aws_iam_role_policy" "comprehend_policy" {
  name = "comprehend-phishing-policy"
  role = aws_iam_role.comprehend_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:ListBucket",
          "s3:PutObject",
          "s3:PutObjectAcl"
        ]
        Resource = [
          aws_s3_bucket.phishing_detection.arn,
          "${aws_s3_bucket.phishing_detection.arn}/*"
        ]
      }
    ]
  })
} 