# Phishing Detection Data

This directory contains data for training and testing the phishing detection model.

## Structure

- **training/** - Contains CSV files used for training the AWS Comprehend custom classification model
- **testing/** - Contains sample data for testing the model after deployment

## Data Format

The training data is in Comprehend CSV format:

```
label,"text"
label,"text"
```

Where:
- `label` is either "phishing" or "nonphishing"
- `text` is the email content to be classified

## Training the Model

To train a custom model in AWS Comprehend:

1. Prepare your CSV file in the format shown above
2. Upload it to the S3 bucket created by Terraform
3. Train a new Comprehend custom classifier following AWS documentation

## Sample Usage

The sample files in this directory are for demonstration purposes only. For production use, we recommend creating a more comprehensive dataset with a variety of phishing and legitimate email examples.

## Important Note

The training data in this directory has been anonymized to remove any personally identifiable information or sensitive content. 