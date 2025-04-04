# Lambda Functions

This directory contains the Lambda function code for the phishing detection system:

## Functions

1. **phishing_detector.py**
   - Main API entry point
   - Handles text analysis requests
   - Uses the endpoint manager to ensure a Comprehend endpoint is available
   - Returns phishing probability scores

2. **phishing_endpoint_manager.py**
   - Manages the Comprehend endpoint lifecycle
   - Creates the endpoint if it doesn't exist
   - Checks the status of existing endpoints
   - Provides the endpoint ARN for classification requests

3. **phishing_endpoint_cleanup.py**
   - Scheduled cleanup function that runs every 5 minutes
   - Finds and deletes idle endpoints older than 60 minutes
   - Helps reduce costs by removing unused endpoints

## Development

To make changes to the Lambda functions:

1. Edit the Python files in this directory
2. Create new ZIP files:
   ```
   powershell -Command "Compress-Archive -Path lambda/phishing_detector.py -DestinationPath lambda/phishing_detector.zip -Force"
   ```
3. Update the Lambda functions via Terraform or the AWS CLI:
   ```
   aws lambda update-function-code --function-name phishing-detector --zip-file fileb://lambda/phishing_detector.zip
   ```

## Deployment

The functions are deployed through Terraform with configurations in:
- `lambda.tf` - Lambda functions and permissions
- `api_gateway.tf` - API Gateway configuration
- `iam.tf` - IAM roles for Comprehend integration 