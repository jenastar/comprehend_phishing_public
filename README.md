# Phishing Detection Tool

This tool spots phishing emails using AI!

[![jenastar/comprehend_phishing_public context](https://badge.forgithub.com/jenastar/comprehend_phishing_public)](https://uithub.com/jenastar/comprehend_phishing_public)

## What This Does

This tool uses AWS to:
- Store training data in S3 buckets
- Run a machine learning model using AWS Comprehend
- Set up an API for checking if emails are phishing attempts
- Clean up resources automatically so we don't waste money

## Setup and Deployment

### Prerequisites

- AWS CLI installed and configured with appropriate permissions
- Terraform installed (version 1.0.0 or higher)
- Basic understanding of AWS services (S3, Lambda, Comprehend, IAM)

### Deployment Steps

1. Clone this repository:
   ```bash
   git clone <your-repo-url>
   cd phishing-detection
   ```

2. Initialize Terraform:
   ```bash
   terraform init
   ```

3. Set your variables in a `terraform.tfvars` file (optional):
   ```
   region = "us-east-1"
   environment = "dev"
   app_id = "YOUR_APP_ID"
   ```

4. Rebuild the Lambda function ZIP files (optional, only if you've modified the Lambda code):
   ```bash
   # On Windows
   powershell -Command "Compress-Archive -Path lambda/phishing_detector.py -DestinationPath lambda/phishing_detector.zip -Force"
   powershell -Command "Compress-Archive -Path lambda/phishing_endpoint_manager.py -DestinationPath lambda/phishing_endpoint_manager.zip -Force"
   powershell -Command "Compress-Archive -Path lambda/phishing_endpoint_cleanup.py -DestinationPath lambda/phishing_endpoint_cleanup.zip -Force"
   
   # On Linux/Mac
   cd lambda
   zip -j phishing_detector.zip phishing_detector.py
   zip -j phishing_endpoint_manager.zip phishing_endpoint_manager.py
   zip -j phishing_endpoint_cleanup.zip phishing_endpoint_cleanup.py
   cd ..
   ```

5. Deploy the infrastructure:
   ```bash
   terraform apply
   ```

6. After deployment, you'll receive an API Gateway URL in the outputs.

## How To Use It

Just send a text message to the API, and it tells you if it's a phishing attempt:

```bash
curl -X POST https://[your-api-endpoint]/prod/detect \
  -H "Content-Type: application/json" \
  -d '{"text": "Your message to analyze"}'
```

You'll get back something like:
```json
{
  "analysis": {
    "phishing_score": 0.9955,  // High score = probably phishing!
    "legitimate_score": 0.0044,
    "is_phishing": true
  }
}
```

## Auto-Cleanup

We don't waste money on idle resources:

1. When you use the API, it automatically creates a special Comprehend endpoint
2. The endpoint costs money while it's running
3. Our cleanup script runs every 5 minutes to check for idle endpoints
4. If an endpoint has been sitting around for more than 60 minutes, it gets deleted automatically
5. Next time someone uses the API, a new endpoint is created

## Retraining the Model

To improve model accuracy with new data:

1. Create a CSV file with the following format:
   ```
   phishing,"This is a phishing email example"
   nonphishing,"This is a legitimate email example"
   ```

2. Upload the CSV file to the S3 bucket:
   ```bash
   aws s3 cp your-new-data.csv s3://[your-phishing-detection-bucket]/training/
   ```

3. Start model retraining:
   Drop your tagged data into the S3 bucket [your-phishing-detection-bucket]/training/PUT_IT_HERE.csv
   Use the AWS UI to retrain the "phishing-detection-model" model with a new version number (vN-phishing-detector), selecting your mode etc.
   Next time you make an API call to the endpoint it will start the endpoint using the latest model.

4. The next time an endpoint is created (automatically when using the API), it will use the latest model version!

## Cost

Based on AWS Comprehend pricing, this project should cost:

- **Endpoint Usage**: $0.0005 per second while running ($1.80/hour)
- **Cleanup Lambda**: Minimal cost (part of Lambda free tier)
- **Text Analysis**: $0.0001 per 100 characters processed
- **Cost Control**: Your cleanup script helps by deleting idle endpoints after 60 minutes
- **Estimate**: For 10,000 documents (550 chars each) = $6 for analysis
- **Optimization**: Increasing MAX_AGE_MINUTES reduces endpoint creation costs
- **Custom Model**: $3/hour for training + $0.50/month for storage

## Project Structure

- `main.tf` - Main Terraform configuration
- `variables.tf` - Variable definitions
- `outputs.tf` - Output values after deployment
- `iam.tf` - IAM roles and policies
- `lambda.tf` - Lambda function configurations
- `s3.tf` - S3 bucket configurations
- `comprehend.tf` - AWS Comprehend resources
- `api_gateway.tf` - API Gateway configuration
- `cloudwatch.tf` - CloudWatch event rules for cleanup
- `lambda/` - Lambda function code
- `data/` - Training and testing data for the model

## License

This project is licensed under the MIT License - see the LICENSE file for details.
