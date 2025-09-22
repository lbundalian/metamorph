#!/usr/bin/env python3
"""
KDK to RD Converter Demo

This demo script converts a KDK (Klinische Dokumentation Krebs) format JSON file
to RD (Rare Disease) format JSON file using the metamorph library.

Usage:
    python main.py <input_kdk_file> [output_rd_file]

Examples:
    python main.py sample/KDK.json
    python main.py sample/KDK.json output/transformed_rd.json
"""

import argparse
import json
import os
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
from metamorph.morphers.kdk_to_rd_morpher import KDKToRDMorpher
from metamorph.utils.validators import DataValidator
from metamorph.utils.rd_schema_converter import RDSchemaConverter


def validate_kdk_file(file_path: str) -> bool:
    """
    Validate that the input file exists and contains valid JSON.
    
    Args:
        file_path: Path to the KDK JSON file
        
    Returns:
        True if file is valid, False otherwise
    """
    if not os.path.exists(file_path):
        print(f"❌ Error: Input file '{file_path}' does not exist.")
        return False
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            json.load(f)
        print(f"✅ Input file '{file_path}' is valid JSON.")
        return True
    except json.JSONDecodeError as e:
        print(f"❌ Error: Invalid JSON in '{file_path}': {e}")
        return False
    except Exception as e:
        print(f"❌ Error reading file '{file_path}': {e}")
        return False


def load_kdk_data(file_path: str) -> dict:
    """
    Load KDK data from JSON file.
    
    Args:
        file_path: Path to the KDK JSON file
        
    Returns:
        Dictionary containing KDK data
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_rd_data(data: dict, file_path: str) -> bool:
    """
    Save RD data to JSON file with pretty formatting.
    
    Args:
        data: RD data dictionary
        file_path: Output file path
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Ensure output directory exists
        output_dir = os.path.dirname(file_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ RD data saved to '{file_path}'")
        return True
    except Exception as e:
        print(f"❌ Error saving to '{file_path}': {e}")
        return False


def print_transformation_summary(kdk_data: dict, rd_data: dict):
    """
    Print a summary of the transformation.
    
    Args:
        kdk_data: Original KDK data
        rd_data: Transformed RD data
    """
    print("\n" + "="*60)
    print("TRANSFORMATION SUMMARY")
    print("="*60)
    
    # Patient information
    patient = rd_data.get('patient', {})
    print(f"Patient ID: {patient.get('id', 'N/A')}")
    print(f"Gender: {patient.get('gender', {}).get('display', 'N/A')}")
    print(f"Birth Date: {patient.get('birthDate', 'N/A')}")
    
    # Handle age safely
    age_info = patient.get('age')
    if age_info and isinstance(age_info, dict):
        age_value = age_info.get('value', 'N/A')
        age_unit = age_info.get('unit', '')
        print(f"Age: {age_value} {age_unit}")
    else:
        print(f"Age: N/A")
    
    # Diagnoses
    diagnoses = rd_data.get('diagnoses', [])
    print(f"\nDiagnoses: {len(diagnoses)} items")
    for i, diagnosis in enumerate(diagnoses, 1):
        codes = diagnosis.get('codes', [])
        if codes:
            main_code = codes[0]
            print(f"  {i}. {main_code.get('code')} - {main_code.get('display', 'No description')}")
    
    # HPO Terms
    hpo_terms = rd_data.get('hpoTerms', [])
    print(f"\nHPO Terms: {len(hpo_terms)} items")
    for i, hpo in enumerate(hpo_terms, 1):
        value = hpo.get('value', {})
        print(f"  {i}. {value.get('code', 'Unknown code')}")
    
    # Care Plans
    care_plans = rd_data.get('carePlans', [])
    print(f"\nCare Plans: {len(care_plans)} items")
    
    # Episodes of Care
    episodes = rd_data.get('episodesOfCare', [])
    print(f"Episodes of Care: {len(episodes)} items")
    
    print("="*60)


def validate_transformation_output(rd_data: dict) -> bool:
    """
    Validate the transformed RD data against the schema.
    
    Args:
        rd_data: Transformed RD data
        
    Returns:
        True if validation passes, False otherwise
    """
    try:
        converter = RDSchemaConverter()
        
        # Validate schema compliance
        is_valid, errors, warnings = converter.validate_schema_compliance(rd_data)
        
        print("\n" + "="*60)
        print("SCHEMA VALIDATION")
        print("="*60)
        
        if is_valid:
            print("✅ Schema validation: PASSED")
        else:
            print("❌ Schema validation: FAILED")
        
        if errors:
            print(f"\n❌ Errors ({len(errors)}):")
            for error in errors:
                print(f"  - {error}")
        
        if warnings:
            print(f"\n⚠️  Warnings ({len(warnings)}):")
            for warning in warnings:
                print(f"  - {warning}")
        
        if not errors and not warnings:
            print("✅ No errors or warnings found")
        
        print("="*60)
        return is_valid
        
    except Exception as e:
        print(f"❌ Error during validation: {e}")
        return False


def main():
    """Main function to handle command line arguments and orchestrate the conversion."""
    parser = argparse.ArgumentParser(
        description="Convert KDK format JSON to RD format JSON",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s sample/KDK.json
  %(prog)s sample/KDK.json output/converted_rd.json
  %(prog)s data/patient123.json results/patient123_rd.json
        """
    )
    
    parser.add_argument(
        'input_file',
        help='Path to the input KDK JSON file'
    )
    
    parser.add_argument(
        'output_file',
        nargs='?',
        help='Path to the output RD JSON file (optional, defaults to <input>_converted.json)'
    )
    
    parser.add_argument(
        '--validate',
        action='store_true',
        help='Validate the output against RD schema'
    )
    
    parser.add_argument(
        '--verbose',
        '-v',
        action='store_true',
        help='Enable verbose output'
    )
    
    args = parser.parse_args()
    
    # Determine output file path
    if args.output_file:
        output_file = args.output_file
    else:
        input_path = Path(args.input_file)
        output_file = str(input_path.parent / f"{input_path.stem}_converted.json")
    
    print("KDK to RD Converter Demo")
    print("="*40)
    print(f"Input file: {args.input_file}")
    print(f"Output file: {output_file}")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*40)
    
    # Validate input file
    if not validate_kdk_file(args.input_file):
        sys.exit(1)
    
    try:
        # Load KDK data
        print("\n📂 Loading KDK data...")
        kdk_data = load_kdk_data(args.input_file)
        
        if args.verbose:
            print(f"✅ Loaded KDK data with {len(str(kdk_data))} characters")
        
        # Initialize the morpher
        print("🔄 Initializing KDK to RD morpher...")
        morpher = KDKToRDMorpher()
        
        # Perform transformation
        print("⚙️  Transforming KDK to RD format...")
        rd_data = morpher.morph(kdk_data)
        
        if args.verbose:
            print(f"✅ Transformation complete - generated {len(str(rd_data))} characters")
        
        # Save RD data
        print("💾 Saving RD data...")
        if not save_rd_data(rd_data, output_file):
            sys.exit(1)
        
        # Print summary
        print_transformation_summary(kdk_data, rd_data)
        
        # Validate output if requested
        if args.validate:
            is_valid = validate_transformation_output(rd_data)
            if not is_valid:
                print("\n⚠️  Warning: Output validation failed, but file was saved.")
        
        print(f"\n🎉 Conversion completed successfully!")
        print(f"📄 Output saved to: {output_file}")
        
    except Exception as e:
        print(f"\n❌ Error during conversion: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()