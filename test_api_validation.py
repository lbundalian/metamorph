#!/usr/bin/env python3
"""
Test API validation using Python requests instead of curl.
"""

import json
import requests
import sys

def test_api_validation(json_file_path: str):
    """Test API validation using requests library."""
    
    # Read the JSON file
    with open(json_file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # API endpoint
    api_url = "https://preview.dnpm-dip.net/api/rd/etl/patient-record:validate"
    
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    
    try:
        print(f"Validating {json_file_path} against API...")
        print("-" * 50)
        
        response = requests.post(api_url, json=data, headers=headers, timeout=30)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            
            if "issues" in result:
                errors = [issue for issue in result["issues"] if issue.get("severity") == "error"]
                warnings = [issue for issue in result["issues"] if issue.get("severity") == "warning"]
                
                if errors:
                    print(f"\n❌ Validation failed with {len(errors)} errors:")
                    for i, error in enumerate(errors, 1):
                        print(f"  {i}. {error.get('message', str(error))}")
                        
                if warnings:
                    print(f"\n⚠️  {len(warnings)} warnings:")
                    for i, warning in enumerate(warnings, 1):
                        print(f"  {i}. {warning.get('message', str(warning))}")
                        
                if not errors:
                    print("\n✅ Validation successful!")
                    return True
                else:
                    return False
            else:
                print("\n✅ Validation successful!")
                return True
        else:
            print(f"\n❌ API request failed with status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_api_validation.py <json_file_path>")
        sys.exit(1)
    
    json_file = sys.argv[1]
    success = test_api_validation(json_file)
    sys.exit(0 if success else 1)