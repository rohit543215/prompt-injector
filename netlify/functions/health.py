import json

def handler(event, context):
    # Handle CORS
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Allow-Methods': 'GET, OPTIONS'
    }
    
    # Handle preflight requests
    if event['httpMethod'] == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': headers,
            'body': ''
        }
    
    return {
        'statusCode': 200,
        'headers': headers,
        'body': json.dumps({
            'status': 'healthy',
            'model_loaded': True,
            'model_type': 'Rule-based + spaCy',
            'supported_pii_types': [
                'PERSON', 'EMAIL', 'PHONE', 'SSN', 'CREDIT_CARD',
                'ADDRESS', 'DATE', 'ORGANIZATION', 'LOCATION', 
                'IP_ADDRESS', 'URL', 'BANK_ACCOUNT'
            ]
        })
    }