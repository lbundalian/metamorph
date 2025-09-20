#!/usr/bin/env python3
"""
Demonstration script showing KDK to RD transformation capabilities.

This script loads the sample KDK data, transforms it to RD format,
and demonstrates the validation capabilities.
"""

import json
import sys
from pathlib import Path

# Add the src directory to the path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent / "src"))

from metamorph import KDKToRDMorpher, KDKSchema, RDSchema
from metamorph.utils import DataValidator, TransformationError, ValidationError


def load_sample_data():
    """Load the sample KDK and RD JSON files."""
    sample_dir = Path(__file__).parent / "sample"
    
    # Load KDK sample
    with open(sample_dir / "KDK.json", "r", encoding="utf-8") as f:
        kdk_data = json.load(f)
    
    # Load RD sample for comparison
    with open(sample_dir / "RD.json", "r", encoding="utf-8") as f:
        rd_data = json.load(f)
    
    return kdk_data, rd_data


def create_test_kdk_data():
    """Create a test KDK data structure with actual values."""
    return {
        "case": {
            "priorDiagnostic": {
                "type": "genetic_testing",
                "date": "2024-01-15"
            },
            "diagnosisOd": {
                "germlineDiagnosisConfirmed": True,
                "hpoTerms": [
                    {
                        "text": "Microcephaly",
                        "system": "https://hpo.jax.org",
                        "code": "HP:0000252",
                        "version": "2024"
                    },
                    {
                        "text": "Intellectual disability",
                        "system": "https://hpo.jax.org", 
                        "code": "HP:0001249",
                        "version": "2024"
                    }
                ],
                "topography": {
                    "system": "https://www.bfarm.de/DE/Kodiersysteme/Terminologien/Alpha-ID-SE",
                    "code": "T001",
                    "version": "2025"
                },
                "histology": {
                    "text": "Genetic disorder",
                    "system": "https://www.bfarm.de/DE/Kodiersysteme/Terminologien/Alpha-ID-SE",
                    "code": "H001",
                    "version": "2025"
                },
                "mainDiagnosis": {
                    "code": "Q87.0",
                    "version": "2025",
                    "date": "2024-03-15",
                    "system": "http://fhir.de/CodeSystem/bfarm/icd-10-gm",
                    "display": "Angeborene Fehlbildungssyndrome mit vorwiegender Beteiligung des Gesichtes"
                },
                "additionalDiagnoses": [
                    {
                        "code": "Q02",
                        "version": "2025",
                        "date": "2024-03-15",
                        "system": "http://fhir.de/CodeSystem/bfarm/icd-10-gm",
                        "display": "Mikrozephalie"
                    }
                ],
                "ecogPerformanceStatusScore": "2",
                "libraryType": "WES"
            }
        },
        "metaData": {
            "gender": "male",
            "mvConsent": {
                "version": "1.0",
                "scope": [
                    {
                        "type": "research",
                        "date": "2024-01-01",
                        "domain": "rare_diseases"
                    }
                ],
                "presentationDate": "2024-01-01"
            },
            "birthDate": "2020-05-15",
            "researchConsents": [],
            "decisionToInclude": True,
            "coverageType": "gesetzliche Krankenversicherung",
            "tanC": "AOK12345",
            "submission": {
                "clinicalDataNodeId": "CDN001",
                "type": "initial",
                "submitterId": "SUB001",
                "genomicDataCenterId": "GDC001",
                "date": "2024-03-20",
                "diseaseType": "rare_disease"
            },
            "molecularBoardDecisionDate": "2024-04-01",
            "addressAGS": "12345"
        },
        "plan": {
            "preventiveMeasures": [
                {
                    "type": "genetic_counseling",
                    "identifier": "GC001"
                },
                {
                    "type": "regular_monitoring",
                    "identifier": "RM001"
                }
            ],
            "carePlanOd": {
                "studyRecommended": True,
                "counsellingRecommended": True,
                "interventionRecommended": False,
                "molecularBoardDecisionDate": "2024-04-01",
                "reEvaluationRecommended": True
            }
        }
    }


def demonstrate_transformation():
    """Demonstrate the KDK to RD transformation process."""
    print("=" * 60)
    print("METAMORPH - KDK to RD Transformation Demonstration")
    print("=" * 60)
    
    # Create test data with actual values
    print("\\n1. Creating test KDK data...")
    kdk_test_data = create_test_kdk_data()
    print(f"   ✓ Created KDK data with patient born {kdk_test_data['metaData']['birthDate']}")
    
    # Validate input data
    print("\\n2. Validating input KDK data...")
    is_valid, errors = DataValidator.validate_kdk_data(kdk_test_data)
    if is_valid:
        print("   ✓ KDK data is valid")
    else:
        print("   ✗ KDK data validation errors:")
        for error in errors:
            print(f"     - {error}")
        return
    
    # Transform data
    print("\\n3. Transforming KDK to RD format...")
    try:
        morpher = KDKToRDMorpher()
        rd_result = morpher.morph(kdk_test_data)
        print("   ✓ Transformation completed successfully")
        
        # Show transformation summary
        patient = rd_result['patient']
        print(f"   ✓ Patient ID: {patient['id']}")
        print(f"   ✓ Patient gender: {patient['gender']['code']} ({patient['gender']['display']})")
        print(f"   ✓ Patient birth date: {patient['birthDate']}")
        print(f"   ✓ Diagnoses created: {len(rd_result['diagnoses'])}")
        print(f"   ✓ HPO terms created: {len(rd_result['hpoTerms'])}")
        print(f"   ✓ Care plans created: {len(rd_result['carePlans'])}")
        
        if patient.get('age'):
            print(f"   ✓ Calculated age: {patient['age']['value']} {patient['age']['unit']}")
            
    except Exception as e:
        print(f"   ✗ Transformation failed: {e}")
        return
    
    # Validate output data
    print("\\n4. Validating output RD data...")
    is_valid, errors = DataValidator.validate_rd_data(rd_result)
    if is_valid:
        print("   ✓ RD data is valid")
    else:
        print("   ✗ RD data validation errors:")
        for error in errors:
            print(f"     - {error}")
    
    # Check transformation quality
    print("\\n5. Checking transformation quality...")
    quality_ok, warnings = DataValidator.validate_transformation_quality(kdk_test_data, rd_result)
    if quality_ok:
        print("   ✓ Transformation quality is good")
    else:
        print("   ⚠ Transformation quality warnings:")
        for warning in warnings:
            print(f"     - {warning}")
    
    # Show sample output
    print("\\n6. Sample transformed data:")
    print("   Patient section:")
    print(f"   {json.dumps(rd_result['patient'], indent=4, ensure_ascii=False)[:300]}...")
    
    if rd_result['diagnoses']:
        print("\\n   First diagnosis:")
        print(f"   {json.dumps(rd_result['diagnoses'][0], indent=4, ensure_ascii=False)[:300]}...")
    
    # Save result
    output_file = Path(__file__).parent / "transformed_result.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(rd_result, f, indent=2, ensure_ascii=False)
    print(f"\\n   ✓ Full result saved to: {output_file}")
    
    print("\\n" + "=" * 60)
    print("TRANSFORMATION DEMONSTRATION COMPLETED")
    print("=" * 60)


def compare_with_sample():
    """Compare our transformation with the provided RD sample."""
    print("\\n" + "=" * 60)
    print("COMPARISON WITH SAMPLE RD DATA")
    print("=" * 60)
    
    try:
        kdk_sample, rd_sample = load_sample_data()
        print("\\n✓ Loaded sample data files")
        
        # The sample KDK has empty fields, so create meaningful test data
        # but show what fields are available for mapping
        print("\\nKDK Sample Structure Analysis:")
        print(f"- Case sections: {list(kdk_sample.get('case', {}).keys())}")
        print(f"- Metadata fields: {list(kdk_sample.get('metaData', {}).keys())}")
        print(f"- Plan sections: {list(kdk_sample.get('plan', {}).keys())}")
        
        print("\\nRD Sample Structure Analysis:")
        print(f"- Top-level sections: {list(rd_sample.keys())}")
        print(f"- Patient fields: {list(rd_sample.get('patient', {}).keys())}")
        print(f"- Number of diagnoses: {len(rd_sample.get('diagnoses', []))}")
        print(f"- Number of HPO terms: {len(rd_sample.get('hpoTerms', []))}")
        print(f"- Number of care plans: {len(rd_sample.get('carePlans', []))}")
        
        # Note about complexity
        print("\\n📋 Transformation Scope:")
        print("✓ Basic patient demographics (gender, birth date, address)")
        print("✓ Diagnosis codes and descriptions")
        print("✓ HPO phenotype terms")
        print("✓ Care plan recommendations")
        print("✓ Health insurance information")
        print("⚠ Complex NGS data, variants, and detailed genetics (not in KDK)")
        print("⚠ Hospitalization details (not in KDK)")
        print("⚠ Complex therapy histories (limited in KDK)")
        
    except FileNotFoundError as e:
        print(f"✗ Could not load sample files: {e}")
    except Exception as e:
        print(f"✗ Error during comparison: {e}")


if __name__ == "__main__":
    try:
        demonstrate_transformation()
        compare_with_sample()
    except KeyboardInterrupt:
        print("\\n\\nDemonstration interrupted by user.")
    except Exception as e:
        print(f"\\n\\nDemonstration failed with error: {e}")
        import traceback
        traceback.print_exc()