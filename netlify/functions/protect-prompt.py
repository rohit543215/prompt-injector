import json
import sys
import os
from pathlib import Path

# Add the parent directories to the path
current_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(current_dir))

from prompt_protector import PromptProtector

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
        prompt = body.get('prompt', '')
        num_alternatives = body.get('num_alternatives', 0)
        
        # Initialize protector
        protector = PromptProtector()
        
        # Generate protected prompt
        result = protector.generate_protected_prompt(prompt)
        
        # Add alternatives if requested
        if num_alternatives and num_alternatives > 0:
            alternatives = protector.generate_alternative_prompts(prompt, num_alternatives)
            result['alternatives'] = alternatives
        
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps(result)
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({'error': str(e)})
        }