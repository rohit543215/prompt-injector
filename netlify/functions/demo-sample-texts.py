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
    
    sample_data = {
        "samples": [
            {
                "title": "Email Sample",
                "text": "Hi John Smith, please contact me at john.doe@email.com or call 555-123-4567. My address is 123 Main St, New York, NY."
            },
            {
                "title": "Business Card",
                "text": "Jane Wilson, CEO of TechCorp Inc. Email: jane.wilson@techcorp.com, Phone: (555) 987-6543, Located in San Francisco, CA."
            },
            {
                "title": "Financial Info",
                "text": "Please process payment using card 4532-1234-5678-9012 or transfer to account GB82-WEST-1234-5698-7654-32 by 2024-12-31."
            },
            {
                "title": "Personal Details",
                "text": "Patient: Mary Johnson, DOB: 1985-03-15, SSN: 123-45-6789, Address: 456 Oak Avenue, Chicago, IL 60601."
            }
        ]
    }
    
    return {
        'statusCode': 200,
        'headers': headers,
        'body': json.dumps(sample_data)
    }