#!/usr/bin/env python3
"""
Standalone Example - Using Metamorph without Package Installation

This example shows how to use the metamorph library directly from the source
without installing it as a package. Simply place this script in the metamorph
project directory and run it.
"""

import os
import sys
import json

# Add the src directory to Python path for direct imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from metamorph.morphers.kdk_to_rd_morpher import KDKToRDMorpher


def main():
    print("🔬 Metamorph Standalone Example")
    print("="*50)
    
    # Example KDK data (minimal structure)
    sample_kdk_data = {
        "case": {
            "diagnosisOd": {
                "germlineDiagnosisConfirmed": True,
                "mainDiagnosis": {
                    "code": "Q87.0",
                    "version": "2025",
                    "date": "2024-03-15",
                    "system": "http://fhir.de/CodeSystem/bfarm/icd-10-gm",
                    "display": "Angeborene Fehlbildungssyndrome"
                },
                "hpoTerms": [
                    {
                        "text": "Microcephaly",
                        "system": "https://hpo.jax.org",
                        "code": "HP:0000252",
                        "version": "2024-09-01"
                    }
                ]
            }
        },
        "metaData": {
            "gender": "male",
            "birthDate": "2020-05-15",
            "coverageType": "GKV"
        }
    }
    
    print("📝 Input KDK Data:")
    print(json.dumps(sample_kdk_data, indent=2))
    print()
    
    # Initialize the morpher
    print("🔄 Initializing KDK to RD morpher...")
    morpher = KDKToRDMorpher()
    
    # Perform transformation
    print("⚙️  Transforming data...")
    rd_result = morpher.morph(sample_kdk_data)
    
    print("✅ Transformation completed!")
    print()
    
    # Display results
    print("📊 Transformation Results:")
    print("-" * 30)
    
    patient = rd_result.get('patient', {})
    print(f"Patient ID: {patient.get('id', 'N/A')}")
    print(f"Gender: {patient.get('gender', {}).get('display', 'N/A')}")
    print(f"Birth Date: {patient.get('birthDate', 'N/A')}")
    
    diagnoses = rd_result.get('diagnoses', [])
    print(f"Diagnoses: {len(diagnoses)} items")
    
    hpo_terms = rd_result.get('hpoTerms', [])
    print(f"HPO Terms: {len(hpo_terms)} items")
    
    care_plans = rd_result.get('carePlans', [])
    print(f"Care Plans: {len(care_plans)} items")
    
    print()
    print("📄 Full RD Output:")
    print(json.dumps(rd_result, indent=2, ensure_ascii=False))
    
    print()
    print("🎉 Standalone example completed successfully!")
    print("💡 No package installation required - just run directly from source!")


if __name__ == "__main__":
    main()