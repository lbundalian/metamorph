#!/usr/bin/env python3
"""
Demonstration of RD Schema Validation and Conversion.

This script shows how to validate RD JSON files against the RD model schema
and convert them to proper RD model objects.
"""

import json
import sys
from pathlib import Path

# Add the src directory to the path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent / "src"))

from metamorph.utils import validate_rd_file, validate_transformation_output, RDSchemaConverter


def demonstrate_rd_validation():
    """Demonstrate RD file validation capabilities."""
    print("=" * 70)
    print("RD SCHEMA VALIDATION DEMONSTRATION")
    print("=" * 70)
    
    # Test files to validate
    test_files = [
        "sample/RD.json",
        "sample/RD_TEST.json", 
        "transformed_result.json"
    ]
    
    for file_path in test_files:
        full_path = Path(__file__).parent / file_path
        
        print(f"\\n📁 Validating: {file_path}")
        print("-" * 50)
        
        if not full_path.exists():
            print(f"   ❌ File not found: {full_path}")
            continue
        
        # Validate the file
        result = validate_rd_file(full_path)
        
        # Display results
        if result["is_valid"]:
            print("   ✅ Schema validation: PASSED")
        else:
            print("   ❌ Schema validation: FAILED")
        
        # Show summary
        summary = result["summary"]
        print(f"   📊 Summary:")
        print(f"      • Patient valid: {summary['patient_valid']}")
        print(f"      • Diagnoses: {summary['diagnoses_count']}")
        print(f"      • HPO terms: {summary['hpo_terms_count']}")
        print(f"      • Care plans: {summary['care_plans_count']}")
        print(f"      • Errors: {summary['total_errors']}")
        print(f"      • Warnings: {summary['total_warnings']}")
        
        # Show errors if any
        if result["errors"]:
            print("   🚨 Errors:")
            for error in result["errors"][:5]:  # Show first 5 errors
                print(f"      • {error}")
            if len(result["errors"]) > 5:
                print(f"      ... and {len(result['errors']) - 5} more errors")
        
        # Show warnings if any
        if result["warnings"]:
            print("   ⚠️  Warnings:")
            for warning in result["warnings"][:3]:  # Show first 3 warnings
                print(f"      • {warning}")
            if len(result["warnings"]) > 3:
                print(f"      ... and {len(result['warnings']) - 3} more warnings")
        
        # Show model object info if valid
        if result["rd_schema"]:
            rd_schema = result["rd_schema"]
            print(f"   🎯 RD Model Object:")
            print(f"      • Patient ID: {rd_schema.patient.id}")
            print(f"      • Birth Date: {rd_schema.patient.birthDate}")
            print(f"      • Gender: {rd_schema.patient.gender.get('code', 'unknown')}")
            
            if rd_schema.diagnoses:
                first_diag = rd_schema.diagnoses[0]
                print(f"      • First diagnosis: {first_diag.codes[0].get('code', 'unknown') if first_diag.codes else 'no codes'}")


def demonstrate_transformation_validation():
    """Demonstrate validation of transformation output."""
    print("\\n\\n" + "=" * 70)
    print("TRANSFORMATION OUTPUT VALIDATION")
    print("=" * 70)
    
    # Load and validate the transformation result
    transformed_file = Path(__file__).parent / "transformed_result.json"
    
    if not transformed_file.exists():
        print("\\n❌ Transformed result file not found. Run demo_transformation.py first.")
        return
    
    print("\\n🔄 Loading transformation result...")
    
    try:
        with open(transformed_file, 'r', encoding='utf-8') as f:
            transformed_data = json.load(f)
        
        print("   ✅ File loaded successfully")
        
        # Validate using the transformation output validator
        result = validate_transformation_output(transformed_data)
        
        print("\\n📋 Transformation Validation Results:")
        print("-" * 40)
        
        if result["is_valid"]:
            print("   ✅ Transformation output is schema-compliant!")
        else:
            print("   ❌ Transformation output has schema violations")
        
        # Detailed analysis
        if result["rd_schema"]:
            rd_schema = result["rd_schema"]
            
            print("\\n📊 Detailed Analysis:")
            print(f"   • Patient model: ✅ Valid")
            print(f"   • Patient ID: {rd_schema.patient.id}")
            print(f"   • Patient gender: {rd_schema.patient.gender}")
            print(f"   • Patient birth date: {rd_schema.patient.birthDate}")
            
            if rd_schema.patient.age:
                print(f"   • Calculated age: {rd_schema.patient.age}")
            
            print(f"\\n   • Diagnoses: {len(rd_schema.diagnoses)} items")
            for i, diag in enumerate(rd_schema.diagnoses[:2]):  # Show first 2
                print(f"     [{i+1}] ID: {diag.id}")
                print(f"         Codes: {len(diag.codes)} diagnosis codes")
                if diag.codes:
                    first_code = diag.codes[0]
                    print(f"         First: {first_code.get('code', 'N/A')} - {first_code.get('display', 'N/A')}")
            
            print(f"\\n   • HPO Terms: {len(rd_schema.hpoTerms)} items")
            for i, hpo in enumerate(rd_schema.hpoTerms[:2]):  # Show first 2
                print(f"     [{i+1}] {hpo.value.get('code', 'N/A')} (recorded: {hpo.recordedOn})")
            
            print(f"\\n   • Care Plans: {len(rd_schema.carePlans)} items")
            for i, cp in enumerate(rd_schema.carePlans):
                print(f"     [{i+1}] Issued: {cp.issuedOn}")
                print(f"         Genetic counseling: {cp.geneticCounselingRecommended}")
                print(f"         Re-evaluation: {cp.reevaluationRecommended}")
                print(f"         Therapy recommendations: {len(cp.therapyRecommendations)}")
        
        # Show any issues
        if result["errors"]:
            print("\\n🚨 Schema Errors:")
            for error in result["errors"]:
                print(f"   • {error}")
        
        if result["warnings"]:
            print("\\n⚠️  Schema Warnings:")
            for warning in result["warnings"]:
                print(f"   • {warning}")
        
        if not result["errors"] and not result["warnings"]:
            print("\\n🎉 Perfect! No errors or warnings found.")
            
    except Exception as e:
        print(f"\\n❌ Error loading transformation result: {e}")


def demonstrate_schema_converter_usage():
    """Show how to use the RDSchemaConverter directly."""
    print("\\n\\n" + "=" * 70)
    print("DIRECT SCHEMA CONVERTER USAGE")
    print("=" * 70)
    
    print("\\n🛠️  Using RDSchemaConverter directly...")
    
    # Create sample RD data
    sample_rd_data = {
        "patient": {
            "id": "test-patient-123",
            "gender": {
                "code": "female",
                "display": "Weiblich",
                "system": "Gender"
            },
            "birthDate": "1990-01-01",
            "address": {
                "municipalityCode": "12345"
            }
        },
        "diagnoses": [
            {
                "id": "diag-1",
                "patient": {"id": "test-patient-123", "type": "Patient"},
                "recordedOn": "2024-01-01",
                "codes": [
                    {
                        "code": "E10.9",
                        "display": "Type 1 diabetes mellitus",
                        "system": "ICD-10-GM"
                    }
                ]
            }
        ],
        "hpoTerms": [],
        "carePlans": []
    }
    
    # Use the converter
    converter = RDSchemaConverter()
    rd_schema, errors, warnings = converter.convert_from_dict(sample_rd_data)
    
    if rd_schema:
        print("   ✅ Conversion successful!")
        print(f"   📋 Patient: {rd_schema.patient.id}")
        print(f"   📋 Gender: {rd_schema.patient.gender['code']}")
        print(f"   📋 Diagnoses: {len(rd_schema.diagnoses)}")
        
        if rd_schema.diagnoses:
            diag = rd_schema.diagnoses[0]
            print(f"   📋 First diagnosis code: {diag.codes[0]['code']}")
    else:
        print("   ❌ Conversion failed")
    
    if errors:
        print("   🚨 Errors:")
        for error in errors:
            print(f"      • {error}")
    
    if warnings:
        print("   ⚠️  Warnings:")
        for warning in warnings:
            print(f"      • {warning}")


if __name__ == "__main__":
    try:
        demonstrate_rd_validation()
        demonstrate_transformation_validation()
        demonstrate_schema_converter_usage()
        
        print("\\n\\n" + "=" * 70)
        print("🎯 VALIDATION DEMONSTRATION COMPLETED")
        print("=" * 70)
        print("\\n📝 Usage Summary:")
        print("• validate_rd_file(path) - Validate RD JSON file")
        print("• validate_transformation_output(data) - Validate transformation result") 
        print("• RDSchemaConverter() - Direct converter for custom validation")
        print("\\n✅ Your transformation outputs can now be validated against RD schema!")
        
    except KeyboardInterrupt:
        print("\\n\\nValidation demonstration interrupted by user.")
    except Exception as e:
        print(f"\\n\\nValidation demonstration failed with error: {e}")
        import traceback
        traceback.print_exc()