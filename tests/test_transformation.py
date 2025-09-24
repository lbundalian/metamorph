#!/usr/bin/env python3
# test KDK to RD transformation with dummy data + API validation

import json
import sys
import os
import subprocess
from pathlib import Path

# add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from metamorph.morphers.kdk_morpher import KDKMorpher
from metamorph.models.kdk import KDK
from metamorph.utils.validate_api import validate_with_api

def load_test_data(filename: str) -> dict:
    # load test data from sample/dummy
    file_path = Path(__file__).parent.parent / "sample" / "dummy" / filename
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_result(data: dict, filename: str, output_dir: str = "output"):
    # save transformation result to file
    output_path = Path(__file__).parent.parent / output_dir / f"transformed_{filename}"
    # create output dir if needed
    output_path.parent.mkdir(exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"Saved transformed result to: {output_path}")
    return str(output_path)

def test_transformation():
    # test KDK to RD transformation with API validation
    print("Starting KDK to RD transformation test with API validation...")
    
    # init morpher
    morpher = KDKMorpher()
    
    # Test with KDK.json
    try:
        print("\n1. Loading KDK.json...")
        kdk_data_path = Path(__file__).parent.parent / "sample" / "dummy" / "KDK.json"
        kdk_obj = KDK(str(kdk_data_path))
        print(f"   Loaded KDK object: {kdk_obj}")
        
        print("\n2. Performing transformation...")
        rd_result = morpher.morph(kdk_obj, 'RD')
        print(f"   Transformation completed. Result keys: {list(rd_result.keys())}")
        
        print("\n3. Validating result locally...")
        is_valid = morpher.validate(rd_result)
        print(f"   Local validation result: {'PASS' if is_valid else 'FAIL'}")
        
        print("\n4. Saving result...")
        output_file = save_result(rd_result, "KDK_to_RD_with_api.json")
        
        print("\n5. Validating against DNPM-DIP API...")
        api_validation = validate_with_api(output_file)
        
        if api_validation.get("validation_successful"):
            print("   ✅ API validation PASSED!")
            if "api_response" in api_validation:
                response = api_validation["api_response"]
                if "errors" in response and not response["errors"]:
                    print("   ✅ No schema validation errors found")
                elif "message" in response:
                    print(f"   📝 API message: {response['message']}")
        else:
            print("   ❌ API validation FAILED!")
            if "error" in api_validation:
                print(f"   Error: {api_validation['error']}")
            if "api_response" in api_validation:
                response = api_validation["api_response"]
                if "errors" in response and response["errors"]:
                    print(f"   Found {len(response['errors'])} validation errors:")
                    for i, error in enumerate(response["errors"][:5], 1):  # Show first 5 errors
                        print(f"     {i}. {error}")
                    if len(response["errors"]) > 5:
                        print(f"     ... and {len(response['errors']) - 5} more errors")
        
        # Print summary
        print("\n=== TRANSFORMATION SUMMARY ===")
        print(f"Patient ID: {rd_result.get('patient', {}).get('id', 'Not found')}")
        print(f"Patient Gender: {rd_result.get('patient', {}).get('gender', {}).get('display', 'Not found')}")
        print(f"Birth Date: {rd_result.get('patient', {}).get('birthDate', 'Not found')}")
        print(f"Number of Diagnoses: {len(rd_result.get('diagnoses', []))}")
        print(f"Number of HPO Terms: {len(rd_result.get('hpoTerms', []))}")
        print(f"Number of Care Plans: {len(rd_result.get('carePlans', []))}")
        print(f"Number of Episodes: {len(rd_result.get('episodesOfCare', []))}")
        print(f"Number of NGS Reports: {len(rd_result.get('ngsReports', []))}")
        print(f"Local Validation: {'✅ PASS' if is_valid else '❌ FAIL'}")
        print(f"API Validation: {'✅ PASS' if api_validation.get('validation_successful') else '❌ FAIL'}")
        
        # Print first diagnosis if exists
        if rd_result.get('diagnoses'):
            first_diag = rd_result['diagnoses'][0]
            print(f"\nFirst Diagnosis:")
            print(f"  ID: {first_diag.get('id', 'N/A')}")
            if first_diag.get('codes'):
                first_code = first_diag['codes'][0]
                print(f"  Code: {first_code.get('code', 'N/A')} ({first_code.get('system', 'N/A')})")
                print(f"  Display: {first_code.get('display', 'N/A')}")
        
        # Print first HPO term if exists
        if rd_result.get('hpoTerms'):
            first_hpo = rd_result['hpoTerms'][0]
            print(f"\nFirst HPO Term:")
            print(f"  ID: {first_hpo.get('id', 'N/A')}")
            if first_hpo.get('value'):
                print(f"  Code: {first_hpo['value'].get('code', 'N/A')}")
                print(f"  Display: {first_hpo['value'].get('display', 'N/A')}")
        
        return is_valid and api_validation.get("validation_successful", False)
        
    except Exception as e:
        print(f"\nERROR: Transformation failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_with_multiple_files():
    # test transformation with multiple files + API validation
    test_files = ["KDK.json"]
    morpher = KDKMorpher()
    
    results = {}
    for filename in test_files:
        try:
            print(f"\n=== Testing {filename} with API Validation ===")
            kdk_data_path = Path(__file__).parent.parent / "sample" / "dummy" / filename
            kdk_obj = KDK(str(kdk_data_path))
            result = morpher.morph(kdk_obj, 'RD')
            is_valid, message = morpher.validate(result)
            
            # Save and validate with API
            output_file = save_result(result, f"from_{filename}")
            api_validation = validate_with_api(output_file)
            
            results[filename] = {
                "success": True,
                "valid": is_valid,
                "api_valid": api_validation.get("validation_successful", False),
                "patient_count": 1 if result.get('patient') else 0,
                "diagnosis_count": len(result.get('diagnoses', [])),
                "hpo_count": len(result.get('hpoTerms', [])),
                "care_plan_count": len(result.get('carePlans', [])),
                "episode_count": len(result.get('episodesOfCare', [])),
                "ngs_count": len(result.get('ngsReports', []))
            }
            
            if api_validation.get("validation_successful"):
                print(f"✅ API validation passed for {filename}")
            else:
                print(f"❌ API validation failed for {filename}")
                if "error" in api_validation:
                    print(f"   Error: {api_validation['error']}")
            
        except Exception as e:
            print(f"Failed to process {filename}: {e}")
            results[filename] = {"success": False, "error": str(e)}
    
    print("\n=== SUMMARY OF ALL TESTS ===")
    for filename, result in results.items():
        if result["success"]:
            local_status = "✅" if result['valid'] else "❌"
            api_status = "✅" if result.get('api_valid', False) else "❌"
            print(f"{filename}:")
            print(f"  Local Validation: {local_status}")
            print(f"  API Validation: {api_status}")
            print(f"  Data: Diagnoses={result['diagnosis_count']}, HPO={result['hpo_count']}, Episodes={result.get('episode_count', 0)}")
        else:
            print(f"✗ {filename}: FAILED - {result.get('error', 'Unknown error')}")

if __name__ == "__main__":
    print("KDK to RD Transformation Test Suite")
    print("===================================")
    
    # Run single test first
    success = test_transformation()
    
    if success:
        print("\n" + "="*50)
        print("Single test passed! Running multi-file test...")
        test_with_multiple_files()
    else:
        print("\nSingle test failed. Please check errors above.")