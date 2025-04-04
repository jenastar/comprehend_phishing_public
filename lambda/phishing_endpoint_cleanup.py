import boto3
import json
import time
import os
from datetime import datetime, timedelta

def lambda_handler(event, context):
    """
    Lambda function to check all Comprehend endpoints and delete those that are:
    1. Older than MAX_AGE_MINUTES
    2. In 'IN_SERVICE' status (active but idle)
    """
    comprehend = boto3.client('comprehend')
    MAX_AGE_MINUTES = 60  # 60 minutes for cleanup
    ENDPOINT_NAME_PREFIX = 'phishing-detector-endpoint'  # Only delete endpoints with this prefix
    
    try:
        # Get caller identity for the current region and account ID
        sts = boto3.client('sts')
        identity = sts.get_caller_identity()
        account_id = identity['Account']
        region = os.environ.get('AWS_REGION', 'us-east-1')
        print(f"Lambda running as: {json.dumps(identity, default=str)}")
        
        # List all endpoints
        print("Listing all Comprehend endpoints...")
        response = comprehend.list_endpoints()
        endpoints = response.get('EndpointPropertiesList', [])
        
        deleted_endpoints = []
        preserved_endpoints = []
        
        print(f"Found {len(endpoints)} Comprehend endpoints")
        
        # If list_endpoints returned nothing, try checking for our specific endpoint directly
        if len(endpoints) == 0:
            try:
                endpoint_name = ENDPOINT_NAME_PREFIX
                endpoint_arn = f"arn:aws:comprehend:{region}:{account_id}:document-classifier-endpoint/{endpoint_name}"
                print(f"Trying direct describe for: {endpoint_arn}")
                
                describe_response = comprehend.describe_endpoint(EndpointArn=endpoint_arn)
                endpoint_props = describe_response.get('EndpointProperties', {})
                
                if endpoint_props:
                    print(f"Found endpoint via direct describe: {json.dumps(endpoint_props, default=str)}")
                    endpoints = [endpoint_props]
            except Exception as e:
                print(f"Could not directly describe endpoint: {str(e)}")
        
        # Check each endpoint
        for endpoint in endpoints:
            try:
                endpoint_name = endpoint.get('EndpointName')
                endpoint_arn = endpoint.get('EndpointArn')
                status = endpoint.get('Status')
                creation_time = endpoint.get('CreationTime')
                
                print(f"Processing endpoint: {endpoint_name}, ARN: {endpoint_arn}, Status: {status}")
                
                # Check if the endpoint name is missing but we have an ARN
                if not endpoint_name and endpoint_arn:
                    # Extract name from ARN
                    try:
                        endpoint_name = endpoint_arn.split('/')[-1]
                        print(f"Extracted endpoint name from ARN: {endpoint_name}")
                    except Exception as extract_err:
                        print(f"Failed to extract name from ARN: {str(extract_err)}")
                
                # Only process endpoints with our prefix
                if not endpoint_name:
                    print(f"Skipping endpoint with no name: {endpoint_arn}")
                    preserved_endpoints.append({'arn': endpoint_arn, 'reason': 'no_name'})
                    continue
                
                if not endpoint_name.startswith(ENDPOINT_NAME_PREFIX):
                    print(f"Skipping endpoint {endpoint_name} (different prefix)")
                    preserved_endpoints.append({'name': endpoint_name, 'reason': 'different_prefix'})
                    continue
                
                # Calculate age in minutes
                if creation_time:
                    age = (datetime.now() - creation_time.replace(tzinfo=None)).total_seconds() / 60
                    print(f"Endpoint age: {age:.1f} minutes")
                else:
                    print("No creation time found for endpoint, setting age to 0")
                    age = 0
                
                # Only delete endpoints that are IN_SERVICE and older than MAX_AGE_MINUTES
                if status == 'IN_SERVICE' and age > MAX_AGE_MINUTES:
                    print(f"Deleting endpoint {endpoint_name} (age: {age:.1f} minutes)")
                    comprehend.delete_endpoint(EndpointArn=endpoint_arn)
                    deleted_endpoints.append({
                        'name': endpoint_name, 
                        'arn': endpoint_arn,
                        'age_minutes': age
                    })
                else:
                    reason = 'not_in_service' if status != 'IN_SERVICE' else 'too_new'
                    print(f"Preserving endpoint {endpoint_name} (status: {status}, age: {age:.1f} minutes)")
                    preserved_endpoints.append({
                        'name': endpoint_name,
                        'status': status,
                        'age_minutes': age,
                        'reason': reason
                    })
            except Exception as endpoint_err:
                print(f"Error processing endpoint: {str(endpoint_err)}")
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'deleted_endpoints': deleted_endpoints,
                'preserved_endpoints': preserved_endpoints,
                'timestamp': str(datetime.now())
            })
        }
        
    except Exception as e:
        print(f"Error cleaning up endpoints: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e)
            })
        } 