import boto3
import json
import time
import os

def lambda_handler(event, context):
    comprehend = boto3.client('comprehend')
    endpoint_name = 'phishing-detector-endpoint'
    
    try:
        # Get caller identity for the current region and account ID
        sts = boto3.client('sts')
        identity = sts.get_caller_identity()
        account_id = identity['Account']
        region = os.environ.get('AWS_REGION', 'us-east-1')
        print(f"Lambda running as: {json.dumps(identity, default=str)}")
        
        # Construct endpoint ARN using identity
        endpoint_arn = f"arn:aws:comprehend:{region}:{account_id}:document-classifier-endpoint/{endpoint_name}"
        print(f"Using endpoint ARN: {endpoint_arn}")
            
        # Try direct describe first (most reliable way to check endpoint)
        try:
            print(f"Checking endpoint directly: {endpoint_arn}")
            describe_response = comprehend.describe_endpoint(EndpointArn=endpoint_arn)
            
            status = describe_response.get('EndpointProperties', {}).get('Status')
            print(f"Endpoint found with status: {status}")
            
            if status == 'IN_SERVICE':
                return {
                    'statusCode': 200,
                    'body': json.dumps({
                        'status': 'ready',
                        'endpoint_arn': endpoint_arn,
                        'message': 'Endpoint is ready for use'
                    })
                }
            elif status == 'CREATING':
                return {
                    'statusCode': 202,
                    'body': json.dumps({
                        'status': 'creating',
                        'endpoint_arn': endpoint_arn,
                        'message': 'Endpoint is being created'
                    })
                }
            else:
                return {
                    'statusCode': 500,
                    'body': json.dumps({
                        'status': 'error',
                        'message': f'Endpoint exists but in unexpected state: {status}'
                    })
                }
        except Exception as e:
            # If ResourceNotFoundException, endpoint doesn't exist
            if 'ResourceNotFoundException' in str(e):
                print(f"Endpoint not found, will create it: {str(e)}")
                
                # Create the endpoint
                try:
                    # Get model ARN from environment variable
                    model_arn = os.environ.get('MODEL_ARN')
                    
                    if not model_arn:
                        # Construct model ARN using account ID and region
                        model_arn = f"arn:aws:comprehend:{region}:{account_id}:document-classifier/phishing-detection-model/version/v1-phishing-detector"
                        print(f"MODEL_ARN not found in environment, using constructed ARN: {model_arn}")
                    else:
                        print(f"Using model ARN from environment: {model_arn}")
                    
                    # Get the latest model version if we have a base model ARN
                    try:
                        # Extract model name from ARN
                        model_name = model_arn.split('/')[-2]
                        print(f"Base model name extracted: {model_name}")
                        
                        # List all model versions
                        versions_response = comprehend.list_document_classifier_versions(
                            DocumentClassifierName=model_name
                        )
                        versions = versions_response.get('DocumentClassifierVersionPropertiesList', [])
                        
                        # Find latest trained version
                        trained_versions = [v for v in versions if v.get('Status') == 'TRAINED']
                        if trained_versions:
                            # Sort by creation time, newest first
                            sorted_versions = sorted(
                                trained_versions,
                                key=lambda x: x.get('SubmitTime', ''),
                                reverse=True
                            )
                            latest_version = sorted_versions[0]
                            model_arn = latest_version.get('DocumentClassifierArn')
                            print(f"Found latest trained model version: {model_arn}")
                    except Exception as version_err:
                        print(f"Error finding latest model version (using provided ARN): {str(version_err)}")
                    
                    print(f"Creating endpoint with model: {model_arn}")
                    response = comprehend.create_endpoint(
                        EndpointName=endpoint_name,
                        ModelArn=model_arn,
                        DesiredInferenceUnits=1
                    )
                    
                    # Check if response contains EndpointArn before trying to access it
                    created_arn = None
                    if response and isinstance(response, dict):
                        created_arn = response.get('EndpointArn')
                        print(f"Endpoint creation started: {created_arn}")
                    else:
                        print(f"Unexpected response format: {response}")
                    
                    return {
                        'statusCode': 202,
                        'body': json.dumps({
                            'status': 'creating',
                            'endpoint_arn': created_arn or endpoint_arn,
                            'message': 'Endpoint creation started'
                        })
                    }
                except Exception as create_err:
                    print(f"Error creating endpoint: {str(create_err)}")
                    
                    # Special case: endpoint already exists but we couldn't see it earlier
                    if "ConflictException" in str(create_err) or "ResourceInUseException" in str(create_err):
                        print("Endpoint appears to exist but we couldn't see it earlier. Retrying direct check.")
                        try:
                            describe_response = comprehend.describe_endpoint(EndpointArn=endpoint_arn)
                            status = describe_response.get('EndpointProperties', {}).get('Status')
                            
                            if status == 'IN_SERVICE':
                                return {
                                    'statusCode': 200,
                                    'body': json.dumps({
                                        'status': 'ready',
                                        'endpoint_arn': endpoint_arn,
                                        'message': 'Endpoint is ready for use'
                                    })
                                }
                            else:
                                return {
                                    'statusCode': 202,
                                    'body': json.dumps({
                                        'status': 'creating',
                                        'endpoint_arn': endpoint_arn,
                                        'message': 'Endpoint exists but is not ready yet'
                                    })
                                }
                        except Exception as retry_err:
                            print(f"Error on retry check: {str(retry_err)}")
                    
                    return {
                        'statusCode': 500,
                        'body': json.dumps({
                            'status': 'error',
                            'message': f'Failed to create endpoint: {str(create_err)}'
                        })
                    }
            else:
                print(f"Error checking endpoint: {str(e)}")
                return {
                    'statusCode': 500,
                    'body': json.dumps({
                        'status': 'error',
                        'message': f'Error checking endpoint: {str(e)}'
                    })
                }
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'status': 'error',
                'message': f'Unexpected error: {str(e)}'
            })
        } 