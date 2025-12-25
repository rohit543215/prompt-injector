#!/usr/bin/env python3
"""
Test script for PII Detection API
"""

import requests
import json

API_BASE = "http://localhost:8000"

def test_api():
    print("🧪 Testing PII Detection API")
    print("=" * 40)
    
    # Test health endpoint
    print("\n1. Testing health endpoint...")
    try:
        response = requests.get(f"{API_BASE}/health")
        if response.status_code == 200:
            health_data = response.json()
            print(f"✅ API Status: {health_data['status']}")
            print(f"✅ Model Type: {health_data['model_type']}")
            print(f"✅ Model Loaded: {health_data['model_loaded']}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return
    
    # Test analysis endpoint
    print("\n2. Testing text analysis...")
    test_text = "Hi John Smith, contact me at john.doe@email.com or call 555-123-4567. My SSN is 123-45-6789."
    
    try:
        response = requests.post(
            f"{API_BASE}/analyze",
            json={"text": test_text}
        )
        
        if response.status_code == 200:
            analysis = response.json()
            print(f"✅ Analysis successful!")
            print(f"   Original: {analysis['original_text'][:50]}...")
            print(f"   Masked: {analysis['masked_text'][:50]}...")
            print(f"   Found {analysis['pii_count']} PII entities:")
            
            for entity in analysis['detected_entities']:
                print(f"     • {entity['text']} → {entity['type']} ({entity['confidence']:.2f})")
                
        else:
            print(f"❌ Analysis failed: {response.status_code}")
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"❌ Analysis error: {e}")
    
    # Test masking endpoint
    print("\n3. Testing PII masking...")
    try:
        response = requests.post(
            f"{API_BASE}/mask",
            json={"text": test_text}
        )
        
        if response.status_code == 200:
            mask_data = response.json()
            print(f"✅ Masking successful!")
            print(f"   Masked text: {mask_data['masked_text']}")
            print(f"   Detected {len(mask_data['detected_entities'])} entities")
        else:
            print(f"❌ Masking failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Masking error: {e}")
    
    # Test sample texts endpoint
    print("\n4. Testing sample texts...")
    try:
        response = requests.get(f"{API_BASE}/demo/sample-texts")
        if response.status_code == 200:
            samples = response.json()
            print(f"✅ Found {len(samples['samples'])} sample texts")
            for sample in samples['samples']:
                print(f"   • {sample['title']}")
        else:
            print(f"❌ Sample texts failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Sample texts error: {e}")
    
    print("\n🎉 API testing completed!")
    print("\n🌐 Access the web interface at: http://localhost:3000")
    print("📚 API documentation at: http://localhost:8000/docs")

if __name__ == "__main__":
    test_api()