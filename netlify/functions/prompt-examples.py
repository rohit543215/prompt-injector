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
    
    examples_data = {
        "examples": [
            {
                "category": "Email Writing",
                "original": "Write an email to John Smith at john.smith@company.com about the quarterly report. His phone is 555-123-4567.",
                "protected": "Write an email to Alex Johnson at user@example.com about the quarterly report. His phone is 555-0123.",
                "risk_level": "MEDIUM"
            },
            {
                "category": "Data Analysis",
                "original": "Analyze customer data for Sarah Wilson, account #123456789, living at 456 Oak St, Chicago.",
                "protected": "Analyze customer data for Customer A, account #XXXX-XXXX-1234, living at 123 Main Street, Anytown, ST 12345.",
                "risk_level": "HIGH"
            },
            {
                "category": "Customer Service",
                "original": "Help resolve complaint from Mike Johnson (mike.j@email.com) about his order #ORD-789.",
                "protected": "Help resolve complaint from Customer B (contact@example.com) about his order #ORD-789.",
                "risk_level": "LOW"
            },
            {
                "category": "Safe Prompt",
                "original": "Explain how to write effective marketing copy for a tech product.",
                "protected": "Explain how to write effective marketing copy for a tech product.",
                "risk_level": "LOW"
            }
        ]
    }
    
    return {
        'statusCode': 200,
        'headers': headers,
        'body': json.dumps(examples_data)
    }