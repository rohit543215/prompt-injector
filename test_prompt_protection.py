#!/usr/bin/env python3
"""
Test script for Prompt Protection API
"""

import requests
import json

API_BASE = "http://localhost:8000"

def test_prompt_protection():
    print("🛡️ Testing Prompt Protection API")
    print("=" * 50)
    
    test_prompts = [
        {
            "name": "Email with PII",
            "prompt": "Write an email to John Smith at john.smith@company.com about the quarterly report. His phone is 555-123-4567."
        },
        {
            "name": "Customer Data Analysis",
            "prompt": "Analyze customer data for Sarah Johnson, account #123456789, living at 456 Oak St, Chicago."
        },
        {
            "name": "Safe Prompt",
            "prompt": "Explain how to write effective marketing copy for a tech product."
        }
    ]
    
    for i, test in enumerate(test_prompts, 1):
        print(f"\n📝 Test {i}: {test['name']}")
        print(f"Original: {test['prompt']}")
        
        try:
            # Test prompt protection
            response = requests.post(
                f"{API_BASE}/protect-prompt",
                json={
                    "prompt": test['prompt'],
                    "num_alternatives": 2
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Protection successful!")
                print(f"Protected: {result['protected_prompt']}")
                print(f"Risk Level: {result['risk_level']}")
                print(f"Context: {result['context']}")
                print(f"PII Found: {result['pii_count']} entities")
                
                if result['replacements_made']:
                    print("Replacements:")
                    for replacement in result['replacements_made']:
                        print(f"  • {replacement['original']} → {replacement['replacement']} ({replacement['type']})")
                
                if result.get('alternatives'):
                    print(f"Alternatives generated: {len(result['alternatives'])}")
                    for j, alt in enumerate(result['alternatives'][:2], 1):
                        print(f"  Alt {j}: {alt}")
                
                print("Top suggestions:")
                for suggestion in result['suggestions'][:2]:
                    print(f"  • {suggestion}")
                    
            else:
                print(f"❌ Protection failed: {response.status_code}")
                print(f"   Error: {response.text}")
                
        except Exception as e:
            print(f"❌ Protection error: {e}")
        
        print("-" * 70)
    
    # Test risk analysis endpoint
    print(f"\n🔍 Testing Risk Analysis...")
    try:
        response = requests.post(
            f"{API_BASE}/analyze-prompt-risk",
            json={"text": "My SSN is 123-45-6789 and credit card is 4532-1234-5678-9012"}
        )
        
        if response.status_code == 200:
            risk_data = response.json()
            print(f"✅ Risk analysis successful!")
            print(f"Risk Level: {risk_data['risk_level']}")
            print(f"PII Count: {risk_data['pii_count']}")
            print(f"Protection Needed: {risk_data['protection_needed']}")
        else:
            print(f"❌ Risk analysis failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Risk analysis error: {e}")
    
    # Test examples endpoint
    print(f"\n📚 Testing Examples...")
    try:
        response = requests.get(f"{API_BASE}/prompt-examples")
        if response.status_code == 200:
            examples = response.json()
            print(f"✅ Found {len(examples['examples'])} example prompts")
            for example in examples['examples']:
                print(f"  • {example['category']}: {example['risk_level']} risk")
        else:
            print(f"❌ Examples failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Examples error: {e}")
    
    print("\n🎉 Prompt Protection testing completed!")
    print("\n🌐 Access the Prompt Protector at: http://localhost:3000/protect")

if __name__ == "__main__":
    test_prompt_protection()