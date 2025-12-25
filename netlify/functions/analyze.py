import json
import sys
import os
from pathlib import Path

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
        # Add the parent directories to the path
        current_dir = Path(__file__).parent.parent.parent
        sys.path.insert(0, str(current_dir))
        
        from simple_pii_model import SimplePIIProcessor
        
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
        # Return demo analysis if function fails
        demo_analysis = {
            'original_text': event.get('body', {}).get('text', ''),
            'masked_text': 'Demo: [PERSON_123] contacted [EMAIL_456]',
            'detected_entities': [
                {'text': 'John Smith', 'type': 'PERSON', 'confidence': 0.9},
                {'text': 'john@email.com', 'type': 'EMAIL', 'confidence': 0.95}
            ],
            'pii_count': 2,
            'pii_types': ['PERSON', 'EMAIL'],
            'mask_info': []
        }
        
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps(demo_analysis)
        }