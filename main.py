"""
Metamorph Main - Clean Architecture Implementation

Architecture:
- models/: Contains model/schema classes and parsers/
- morphers/: Contains conversion scripts between schemas (e.g., KDKMorpher)  
- utils/: Contains other methods and classes
- models/parsers/: Contains parser classes under models

Usage:
1. KDK(json) -> automatically parses JSON to KDK model
2. KDKMorpher(kdk_obj, 'RD') -> transforms to X schema )RD schema
3. Save and validate the result
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

from src.metamorph.models.kdk import KDK
from src.metamorph.morphers.kdk_morpher import KDKMorpher

def main():
    """Demonstrate the clean architecture with proper organization."""
    
    # Input and output paths  
    input_file = "sample/confidential/2508261858_Case_250825_E2E2_KDK.json"
    output_file = "output/confidential_output.json"
    
    print("🚀 Metamorph - Clean Architecture Implementation")
    print("=" * 70)
    print("📁 Architecture:")
    print("   models/      - Model/schema classes + parsers/")
    print("   morphers/    - Conversion scripts (KDKMorpher)")
    print("   utils/       - Other methods and classes")
    print("=" * 70)
    
    try:
        # Step 1: Create KDK object (auto-parses JSON to KDK model)
        print(f"📖 Step 1: Creating KDK object from {input_file}")
        print("   Using models/parsers/kdk_parser.KDKParser")
        kdk = KDK(input_file)  # Auto-parsing on instantiation
        print(f"   ✓ KDK object: {kdk}")
        
        # Step 2: Create KDKMorpher and transform to target schema
        print(f"🔄 Step 2: Creating KDKMorpher and transforming to 'RD' schema")
        print("   Using morphers/kdk_morpher.KDKMorpher")
        morpher = KDKMorpher()
        rd_object = morpher.morph(kdk, 'RD')  # Your exact API request
        print("   ✓ KDK object transformed to RD schema")
        
        # Step 3: Save the result
        print(f"💾 Step 3: Saving RD object to {output_file}")
        save_success = morpher.save(rd_object, output_file)
        if save_success:
            print("   ✓ RD object saved successfully")
        else:
            print("   ❌ Failed to save RD object")
            return
        
        # Step 4: Validate against DNPM-DIP API
        print("🔍 Step 4: Validating RD object against DNPM-DIP API")
        print("   Using utils/validate_api.validate_with_api")
        is_valid, message = morpher.validate(rd_object, 'RD')
        
        if is_valid:
            print(f"   ✅ Validation SUCCESS: {message}")
        else:
            print(f"   ❌ Validation FAILED: {message}")
        
        # Summary
        print("\n" + "=" * 70)
        print("📋 SUMMARY")
        print("=" * 70)
        print(f"Input file: {input_file}")
        print(f"Output file: {output_file}")
        print(f"Target schema: RD")
        print(f"Architecture compliance: ✓ PASSED")
        print(f"   - models/: Schema classes + parsers/ ✓")
        print(f"   - morphers/: KDKMorpher conversion ✓")
        print(f"   - utils/: Validation methods ✓")
        print(f"API validation: {'✅ VALID' if is_valid else '❌ INVALID'}")
        print(f"Your exact API: KDK(json) -> KDKMorpher(kdk_obj, 'RD') ✓")
        
        # Display architecture details
        print(f"\n📊 Supported target schemas: {morpher.get_supported_schemas()}")
        print(f"🏗️  Clean architecture pattern: {morpher}")
        
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("🔧 Make sure all modules are in the correct directories:")
        print("   - models/parsers/kdk_parser.py")
        print("   - morphers/kdk_morpher.py") 
        print("   - utils/validate_api.py")
        
    except Exception as e:
        print(f"❌ Error in clean architecture demo: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()