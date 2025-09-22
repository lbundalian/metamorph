#!/usr/bin/env python3
import json

# Read the converted file
with open('sample/dummy/KDK_converted.json', 'r') as f:
    data = json.load(f)

print("=== VARIANT IDs ===")
for ngs_report in data.get('ngsReports', []):
    results = ngs_report.get('results', {})
    
    print("\nSmall Variants:")
    for sv in results.get('smallVariants', []):
        print(f"  ID: {sv.get('id')}")
    
    print("\nCopy Number Variants:")
    for cnv in results.get('copyNumberVariants', []):
        print(f"  ID: {cnv.get('id')}")
    
    print("\nStructural Variants:")
    for stv in results.get('structuralVariants', []):
        print(f"  ID: {stv.get('id')}")

print("\n=== REFERENCED VARIANT IDs ===")
for care_plan in data.get('carePlans', []):
    print(f"\nCare Plan ID: {care_plan.get('id')}")
    
    # Check therapy recommendations
    for therapy_rec in care_plan.get('therapyRecommendations', []):
        print(f"  Therapy Recommendation ID: {therapy_rec.get('id')}")
        for sv in therapy_rec.get('supportingVariants', []):
            variant_ref = sv.get('variant', {})
            print(f"    Referenced Variant ID: {variant_ref.get('id')}")
    
    # Check study enrollment recommendations
    for study_rec in care_plan.get('studyEnrollmentRecommendations', []):
        print(f"  Study Recommendation ID: {study_rec.get('id')}")
        for sv in study_rec.get('supportingVariants', []):
            variant_ref = sv.get('variant', {})
            print(f"    Referenced Variant ID: {variant_ref.get('id')}")

print("\n=== THERAPY REFERENCE IDs ===")
for therapy in data.get('therapies', []):
    for history in therapy.get('history', []):
        based_on = history.get('basedOn', {})
        print(f"  Therapy based on ID: {based_on.get('id')}")