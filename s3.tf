resource "aws_s3_bucket" "phishing_detection" {
  bucket = "phishing-detection-${data.aws_caller_identity.current.account_id}"
  
  tags = {
    Name        = "Phishing Detection Data"
    Environment = var.environment
    Project     = "Phishing Detection"
    AppID       = var.app_id
  }
}

resource "aws_s3_bucket_versioning" "phishing_detection" {
  bucket = aws_s3_bucket.phishing_detection.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "phishing_detection" {
  bucket = aws_s3_bucket.phishing_detection.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "phishing_detection" {
  bucket = aws_s3_bucket.phishing_detection.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# Upload training data
resource "aws_s3_object" "training_data" {
  bucket = aws_s3_bucket.phishing_detection.id
  key    = "training/email-trainingdata.csv"
  source = "data/training/email-trainingdata.csv"
  etag   = filemd5("data/training/email-trainingdata.csv")
}

# Create output directory
resource "aws_s3_object" "output_directory" {
  bucket = aws_s3_bucket.phishing_detection.id
  key    = "output/"
  content_type = "application/x-directory"
} 