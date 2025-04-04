import boto3
import json
import time

def invoke_endpoint_manager():
    print("Invoking endpoint manager Lambda function")
    lambda_client = boto3.client('lambda')
    try:
        response = lambda_client.invoke(
            FunctionName='phishing-endpoint-manager',
            InvocationType='RequestResponse'
        )
        payload = response['Payload'].read().decode('utf-8')
        print(f"Endpoint manager response: {payload}")
        return json.loads(payload)
    except Exception as e:
        print(f"Error invoking endpoint manager: {str(e)}")
        raise

def lambda_handler(event, context):
    comprehend = boto3.client('comprehend')
    
    try:
        print(f"Received event: {json.dumps(event)}")
        
        # Parse the incoming request
        if not event.get('body'):
            print("Missing body in event")
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'  # Enable CORS
                },
                'body': json.dumps({
                    'error': 'Missing body in request'
                })
            }
            
        try:
            body = json.loads(event['body'])
            print(f"Parsed body: {json.dumps(body)}")
        except Exception as e:
            print(f"Failed to parse body: {str(e)}")
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'  # Enable CORS
                },
                'body': json.dumps({
                    'error': f'Invalid JSON in request body: {str(e)}'
                })
            }
            
        text = body.get('text')
        
        if not text:
            print("Missing text in request body")
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'  # Enable CORS
                },
                'body': json.dumps({
                    'error': 'Missing text in request body'
                })
            }
        
        # Check endpoint status
        print("Checking endpoint status")
        endpoint_response = invoke_endpoint_manager()
        
        if not endpoint_response or not isinstance(endpoint_response, dict):
            print(f"Invalid endpoint response format: {endpoint_response}")
            return {
                'statusCode': 500,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'  # Enable CORS
                },
                'body': json.dumps({
                    'error': 'Invalid endpoint response format',
                    'details': str(endpoint_response)
                })
            }
            
        if not endpoint_response.get('body'):
            print(f"Missing body in endpoint response: {endpoint_response}")
            return {
                'statusCode': 500,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'  # Enable CORS
                },
                'body': json.dumps({
                    'error': 'Missing body in endpoint response',
                    'details': str(endpoint_response)
                })
            }
            
        try:
            endpoint_body = json.loads(endpoint_response['body'])
            print(f"Endpoint body: {json.dumps(endpoint_body)}")
        except Exception as e:
            print(f"Failed to parse endpoint body: {str(e)}")
            return {
                'statusCode': 500,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'  # Enable CORS
                },
                'body': json.dumps({
                    'error': f'Failed to parse endpoint response: {str(e)}',
                    'raw_response': str(endpoint_response)
                })
            }
        
        if endpoint_response.get('statusCode') == 202:
            # Endpoint is being created, return a friendly message to try again later
            return {
                'statusCode': 202,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'  # Enable CORS
                },
                'body': json.dumps({
                    'status': 'in_progress',
                    'message': 'The endpoint is being created. Please try again in a few minutes.',
                    'details': endpoint_body
                })
            }
        elif endpoint_response.get('statusCode') != 200:
            # Some other error occurred
            return {
                'statusCode': endpoint_response.get('statusCode', 500),
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'  # Enable CORS
                },
                'body': json.dumps({
                    'error': 'Endpoint not ready',
                    'details': endpoint_body
                })
            }
        
        # Check for required endpoint ARN
        endpoint_arn = endpoint_body.get('endpoint_arn')
        if not endpoint_arn:
            print(f"Missing endpoint_arn in response: {endpoint_body}")
            return {
                'statusCode': 500,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'  # Enable CORS
                },
                'body': json.dumps({
                    'error': 'Missing endpoint ARN in response',
                    'details': endpoint_body
                })
            }
        
        # Use the endpoint for analysis
        print(f"Calling classify_document with endpoint: {endpoint_arn}, text length: {len(text)}")
        response = comprehend.classify_document(
            EndpointArn=endpoint_arn,
            Text=text
        )
        
        print(f"Classification response: {json.dumps(response, default=str)}")
        
        # Format the response
        if not response.get('Classes'):
            print(f"Missing Classes in response: {response}")
            return {
                'statusCode': 500,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'  # Enable CORS
                },
                'body': json.dumps({
                    'error': 'Missing classification results',
                    'raw_response': response
                })
            }
        
        classes = response['Classes']
        
        try:
            phishing_score = next((c['Score'] for c in classes if c['Name'] == 'phishing'), 0)
            legitimate_score = next((c['Score'] for c in classes if c['Name'] == 'legitimate'), 0)
        except Exception as e:
            print(f"Error extracting scores: {str(e)}, classes: {classes}")
            return {
                'statusCode': 500,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'  # Enable CORS
                },
                'body': json.dumps({
                    'error': f'Error extracting classification scores: {str(e)}',
                    'classes': classes
                })
            }
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'  # Enable CORS
            },
            'body': json.dumps({
                'analysis': {
                    'phishing_score': phishing_score,
                    'legitimate_score': legitimate_score,
                    'is_phishing': phishing_score > 0.5
                },
                'raw_response': response
            })
        }
        
    except Exception as e:
        print(f"Unexpected error in lambda_handler: {str(e)}")
        import traceback
        traceback.print_exc()
        
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'  # Enable CORS
            },
            'body': json.dumps({
                'error': str(e)
            })
        } 