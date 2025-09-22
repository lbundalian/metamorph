#!/usr/bin/env python3
"""
API Validation Script for DNPM-DIP RD Schema
This script validates transformed JSON files against the DNPM-DIP API endpoint.
"""

import json
import subprocess
import sys
import os
from pathlib import Path

def validate_with_api(json_file_path: str, api_url: str = "https://preview.dnpm-dip.net/api/rd/etl/patient-record:validate") -> dict:
    """
    Validate JSON file against DNPM-DIP API using curl command.
    
    Args:
        json_file_path: Path to the JSON file to validate
        api_url: API endpoint URL for validation
        
    Returns:
        dict: Validation response from the API
    """
    
    if not os.path.exists(json_file_path):
        print(f"Error: File {json_file_path} does not exist")
        return {"error": "File not found"}
    
    try:
        # Prepare curl command
        curl_command = [
            "curl",
            "-X", "POST",
            "-H", "Content-Type: application/json",
            "-H", "Accept: application/json",
            "--data-binary", f"@{json_file_path}",
            api_url
        ]
        
        print(f"Validating {json_file_path} against {api_url}")
        print(f"Running: {' '.join(curl_command)}")
        print("-" * 50)
        
        # Execute curl command
        result = subprocess.run(curl_command, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            try:
                response = json.loads(result.stdout)
                # Check if there are issues (errors)
                if "issues" in response:
                    errors = [issue for issue in response["issues"] if issue.get("severity") == "error"]
                    if errors:
                        return {
                            "validation_successful": False,
                            "api_response": response,
                            "errors": [issue.get("message", str(issue)) for issue in errors]
                        }
                    else:
                        return {
                            "validation_successful": True,
                            "api_response": response
                        }
                else:
                    return {
                        "validation_successful": True,
                        "api_response": response
                    }
            except json.JSONDecodeError:
                return {"error": "Invalid JSON response", "raw_response": result.stdout}
        else:
            return {
                "error": "Curl command failed",
                "return_code": result.returncode,
                "stderr": result.stderr,
                "stdout": result.stdout
            }
            
    except subprocess.TimeoutExpired:
        return {"error": "Request timed out"}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}

def main():
    """Main function to run validation."""
    
    if len(sys.argv) < 2:
        print("Usage: python validate_api.py <json_file_path>")
        print("Example: python validate_api.py transformed_result.json")
        sys.exit(1)
    
    json_file = sys.argv[1]
    api_url = "https://preview.dnpm-dip.net/api/rd/etl/patient-record:validate"
    
    # Allow custom API URL as second argument
    if len(sys.argv) > 2:
        api_url = sys.argv[2]
    
    # Validate
    response = validate_with_api(json_file, api_url)
    
    print("API Validation Response:")
    print("=" * 50)
    print(json.dumps(response, indent=2, ensure_ascii=False))
    
    # Check if validation was successful
    if "error" in response:
        print(f"\n❌ Validation failed with error: {response['error']}")
        sys.exit(1)
    elif "errors" in response and response["errors"]:
        print(f"\n❌ Schema validation failed with {len(response['errors'])} errors")
        sys.exit(1)
    else:
        print("\n✅ Validation successful!")
        sys.exit(0)

if __name__ == "__main__":
    main()