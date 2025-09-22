#!/usr/bin/env python3
"""
Simple API format validation test using urllib (built-in).
"""

import json
import urllib.request
import urllib.parse
import ssl
import sys

def test_api_format(json_file_path: str):
    """Test API format using urllib."""
    
    # Read the JSON file
    with open(json_file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # API endpoint
    api_url = "https://preview.dnpm-dip.net/api/rd/etl/patient-record:validate"
    
    # Convert data to bytes
    json_data = json.dumps(data).encode('utf-8')
    
    # Create request
    req = urllib.request.Request(
        api_url,
        data=json_data,
        headers={
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        },
        method='POST'
    )
    
    try:
        print(f"Testing API format for: {json_file_path}")
        print("-" * 50)
        
        # Create SSL context that doesn't verify certificates (for testing)
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        # Make request
        with urllib.request.urlopen(req, context=ssl_context, timeout=30) as response:
            response_data = response.read().decode('utf-8')
            
            print(f"Status: {response.status}")
            print(f"Raw Response: {response_data}")
            
            if response_data.strip() == "Valid":
                print("\n✅ API Validation successful!")
                return True
            elif not response_data.strip():
                print("\n✅ Empty response - validation successful!")
                return True
            
            try:
                result = json.loads(response_data)
                print(f"Parsed Response: {json.dumps(result, indent=2, ensure_ascii=False)}")
                
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
                            
                    return len(errors) == 0
                else:
                    print("\n✅ No validation issues found!")
                    return True
            except json.JSONDecodeError:
                print(f"\n❌ Could not parse response as JSON: {response_data}")
                return False
                
    except urllib.error.HTTPError as e:
        error_data = e.read().decode('utf-8')
        print(f"\n❌ HTTP Error {e.code}: {e.reason}")
        print(f"Response: {error_data}")
        return False
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python simple_api_test.py <json_file_path>")
        sys.exit(1)
    
    json_file = sys.argv[1]
    success = test_api_format(json_file)
    print(f"\nResult: {'SUCCESS' if success else 'FAILED'}")