import json
import sys
import os
from pathlib import Path

# Add the parent directories to the path
current_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(current_dir))

from simple_pii_model import SimplePIIProcessor

def handler(event, context):
    # Handle CORS
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Allow-Methods': 'POST, OPTIONS'
    }
    
    # Handle preflight requests
    if event['httpMethod'] == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': headers,
            'body': ''
        }
    
    try:
        # Parse request body
        body = json.loads(event['body'])
        text = body.get('text', '')
        
        # Initialize processor
        processor = SimplePIIProcessor()
        
        # Analyze text
        analysis = processor.analyze_text(text)
        
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps(analysis)
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({'error': str(e)})
        }